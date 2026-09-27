"""toast-notify handler：Windows 桌面通知（windows-toasts / WinRT，进程内直发）。

API 依据（Context7 官方文档 windows-toasts 1.3.1）+ 独立评审意见修正：
- 单例 toaster + Lock 双检（评审 F2：post_llm_call 每回合在新 worker 线程上跑，
  per-thread 缓存永不命中且 ident 复用会交叉污染，故不做线程局部缓存）；
- 投递放专用 daemon 短线程（评审 F3：pre_approval_request 在审批面板渲染前于调用方
  线程同步执行，WinRT 首帧初始化绝不允许挂住审批 UI），回调本身毫秒级返回；
- 失败静默但首错必告警（评审 F5：模块级 _warned 去重的一次 logger.warning，
  保住唯一诊断信号，仍绝不上抛）。

用户裁定（2026-09-22）：通知正文**原样输出**，不做脱敏、不做 Bidi/零宽清洗——
仅保留让 toast 能正常渲染的最小处理（换行折叠、控制符剔除、截断）。

设计约束（不变）：纯观察者（返回值恒 None）；无子进程、无 shell；通知失败不拖垮回合。
"""

import logging
import threading

logger = logging.getLogger(__name__)

_CLEAN_MAX = 160

_lock = threading.Lock()
_toaster = None
_warned = False


def _warn_once(exc):
    global _warned
    if not _warned:
        _warned = True
        logger.warning("toast-notify delivery failed (further failures silent)", exc_info=exc)


def _clean(text, limit):
    """最小处理：换行折叠 + 剔除 C0 控制符 + 截断（保证 toast 可渲染），其余原样。"""
    text = str(text or "")[: limit * 4].replace("\r", " ").replace("\n", " ")
    text = "".join(ch for ch in text if ch >= " " and ch != "\x7f").strip()
    if len(text) > limit:
        text = text[: limit - 1] + "…"
    return text or "（无内容）"


def _get_toaster():
    global _toaster
    with _lock:
        if _toaster is None:
            from windows_toasts import WindowsToaster

            _toaster = WindowsToaster("Hermes Agent")
    return _toaster


def _deliver(title, body):
    try:
        from windows_toasts import Toast, ToastDuration

        toast = Toast(
            text_fields=[_clean(title, 60), _clean(body, _CLEAN_MAX)],
            duration=ToastDuration.Long,  # ~25s；默认 Short(~7s) 用户实测来不及看
        )
        _get_toaster().show_toast(toast)
    except Exception as exc:
        _warn_once(exc)


def _send(title, body):
    """专用 daemon 短线程投递：调用方（含审批路径）立即返回（评审 F3）。"""
    try:
        threading.Thread(
            target=_deliver, args=(title, body), daemon=True, name="toast-notify-deliver"
        ).start()
    except Exception as exc:
        _warn_once(exc)  # 连线程都起不了（极端资源枯竭），同样静默降级+首告警


def on_post_llm_call(*, platform=None, assistant_response=None, session_id="", **kwargs):
    """一轮回复完成（agent/turn_finalizer 每回合一次）。仅 CLI 平台。"""
    if platform != "cli":
        return None
    _send("Hermes 回复完成", assistant_response)
    return None


def on_pre_approval_request(*, surface=None, command="", description="", **kwargs):
    """CLI 审批弹窗即将出现（阻塞等待用户前触发）。仅 surface=cli。
    注：载荷原样输出；审批命令若被脱敏是框架 redact_cli 的行为，与本插件无关。"""
    if surface != "cli":
        return None
    detail = command or description or ""
    _send("Hermes 等待审批", detail)
    return None
