"""write-guard: 拦截一切引用系统临时目录的工具调用。

规则（用户指定，2026-09-07）：命令/代码/路径中出现临时目录字样
（/tmp、\\Temp、$TMP、$TEMP、%TEMP% 等）即直接拒绝。
不分析意图、不区分用途、不管重定向还是 tee，命中即 block。

覆盖工具：
  terminal      — 检查 command 参数（shell 模式组，含 mktemp）
  execute_code  — 检查 code 参数（shell 模式组 + Python tempfile API）
  write_file/patch — 检查 path 参数
  其他工具      — 兜底扫描 args 中全部字符串值（如 chrome 截图 filePath）
"""

import logging
import re

logger = logging.getLogger(__name__)

# 通用模式组：路径字样 + 环境变量引用（IGNORECASE，Windows 路径大小写不敏感）
_BLOCK_PATTERNS = [
    # unix / MSYS 风格：/tmp、/tmp/xxx、/var/tmp、/usr/tmp
    # (?![\w-]) 防误伤连字符目录名（如 workspace/tmp-reports）
    r"/tmp(?![\w-])",
    # windows 反斜杠风格：\tmp、C:\tmp
    r"\\tmp(?![\w-])",
    # temp 作为路径组件：$LOCALAPPDATA/Temp、C:\Users\x\AppData\Local\Temp、…\Temp 结尾
    r"[\\/]temp(?:[\\/]|$)",
    # 环境变量引用：$TMPDIR ${TMPDIR}
    r"\$\{?tmpdir\}?(?![\w])",
    # $TMP ${TMP}
    r"\$\{?tmp\}?(?![\w])",
    # $TEMP ${TEMP}
    r"\$\{?temp\}?(?![\w])",
    # cmd 风格：%TEMP% %TMP%
    r"%temp%",
    r"%tmp%",
    # powershell 风格：$env:TEMP $env:TMP
    r"env:(?:temp|tmp)\b",
]

# 仅 shell 命令追加：裸 mktemp 默认写 /tmp
_SHELL_ONLY_PATTERNS = [
    r"\bmktemp\b",
]

# 仅代码追加：Python 标准库临时目录 API（默认写系统 Temp）
_CODE_ONLY_PATTERNS = [
    r"\btempfile\b",
    r"\bgettempdir\b",
    r"\bTemporaryDirectory\b",
    r"\bNamedTemporaryFile\b",
    # Python 读取临时目录环境变量：os.environ["TMP"] / os.environ.get('TEMP') / os.getenv("TMPDIR")
    r"(?:os\.environ(?:\.get)?\s*[\[(]|os\.getenv\s*\()\s*['\"](?:TMPDIR|TMP|TEMP)['\"]",
]

_COMPILED = {
    "shell": [
        re.compile(p, re.IGNORECASE) for p in _BLOCK_PATTERNS + _SHELL_ONLY_PATTERNS
    ],
    "code": [
        re.compile(p, re.IGNORECASE) for p in _BLOCK_PATTERNS + _CODE_ONLY_PATTERNS
    ],
}

# 工具名 → (检查的参数名, 模式组)
_TOOL_ARG_MAP = {
    "terminal": ("command", "shell"),
    "execute_code": ("code", "code"),
    "write_file": ("path", "shell"),
    "patch": ("path", "shell"),
}

_DENIED_MESSAGE = (
    "write-guard 拦截：内容中出现系统临时目录引用（命中：{hit}）。"
    "用户规则：一切临时文件/下载只准写 D:\\myagent\\workspace\\"
    "（Hermes 配置目录 D:\\myagent\\.hermes 除外），"
    "禁止写系统临时目录。请改用工作区路径后重试。"
)


def _scan(kind: str, text: str):
    """返回命中的模式原文，未命中返回 None。"""
    for pat in _COMPILED[kind]:
        m = pat.search(text)
        if m:
            return m.group(0)
    return None


def on_pre_tool_call(tool_name: str, args: dict, task_id: str = "", **kwargs):
    """pre_tool_call hook：命中临时目录模式 → block，未命中 → 放行。"""
    mapped = _TOOL_ARG_MAP.get(tool_name)
    if mapped is not None:
        arg_name, kind = mapped
        text = args.get(arg_name)
        if not isinstance(text, str) or not text:
            logger.debug("write-guard: %s.%s 无内容，放行", tool_name, arg_name)
            return None
        hit = _scan(kind, text)
    else:
        # 兜底：扫描该工具 args 中所有字符串值（如 chrome 截图 filePath）
        kind = "code"
        hit = None
        for value in args.values():
            if isinstance(value, str):
                hit = _scan(kind, value)
                if hit is not None:
                    break
        if hit is None:
            logger.debug("write-guard: %s 未命中临时目录模式，放行", tool_name)
            return None

    if hit is None:
        logger.debug("write-guard: %s 未命中临时目录模式，放行", tool_name)
        return None

    message = _DENIED_MESSAGE.format(hit=hit)
    logger.warning(
        "write-guard: 拦截 %s（task=%s）— 命中模式 %r", tool_name, task_id, hit
    )
    return {"action": "block", "message": message}
