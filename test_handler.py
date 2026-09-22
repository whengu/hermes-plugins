"""write-guard handler 单元测试：真实调用 handler._scan / on_pre_tool_call。

运行：python D:/myagent/workspace/write-guard/test_handler.py
只读测试（无磁盘写入），全部断言通过输出 ALL PASS，退出码 0。
"""

import importlib.util
import sys

HANDLER_PATH = r"D:\myagent\workspace\write-guard\handler.py"
spec = importlib.util.spec_from_file_location("write_guard_handler", HANDLER_PATH)
assert spec is not None and spec.loader is not None
handler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handler)

# (kind, 输入, 期望拦截)
CASES = [
    # --- 本会话真实违规命令，必须拦截 ---
    ("shell", 'curl -sL "https://z.ai/blog" -o "$LOCALAPPDATA/Temp/glm53flash.html"', True),
    ("shell", 'curl -sL "https://z.ai/blog/assets/glm.js" -o "$LOCALAPPDATA/Temp/glm_blog.js"', True),
    # --- 各类临时目录写法，必须拦截 ---
    ("shell", 'curl -o /tmp/out.html https://example.com', True),
    ("shell", 'echo hi > /var/tmp/x.log', True),
    ("shell", 'echo hi > %TEMP%\\x.txt', True),
    ("shell", 'echo hi > %TMP%\\x.txt', True),
    ("shell", 'curl https://x.com -o $TMPDIR/a.js', True),
    ("shell", 'curl https://x.com -o ${TMP}/a.js', True),
    ("shell", 'node run.js 2>&1 | tee $env:TEMP\\log.txt', True),
    ("shell", 'cp a.txt "C:\\Users\\guwh\\AppData\\Local\\Temp\\x"', True),
    ("shell", 'curl -o "C:/Users/guwh/AppData/Local/Temp/x" https://x.com', True),
    ("shell", 'mktemp -d', True),
    ("shell", 'ls C:\\Temp', True),
    # --- 代码类，必须拦截 ---
    ("code", 'import tempfile; tempfile.mkstemp()', True),
    ("code", 'open("/tmp/x", "w").write("hi")', True),
    ("code", 'path = os.environ["TMPDIR"]', True),
    ("code", 'p = tempfile.gettempdir()', True),
    ("code", 'with tempfile.TemporaryDirectory() as d: pass', True),
    # --- 路径参数，必须拦截 ---
    ("shell", 'C:\\Users\\guwh\\AppData\\Local\\Temp\\a.md', True),
    ("shell", 'C:/Users/guwh/AppData/Local/Temp', True),
    # --- 合法命令，必须放行 ---
    ("shell", 'curl -sL "https://z.ai/blog" -o D:/myagent/workspace/blog.html', False),
    ("shell", 'ls /d/myagent/workspace', False),
    ("shell", 'python D:/myagent/workspace/write-guard/test_handler.py', False),
    ("shell", 'git -C D:/Project/guwh/hermes-agent status', False),
    ("shell", 'ls /d/myagent/workspace/tmp-reports', False),  # 连字符目录名防误伤
    ("code", 'print(sum(range(10)))', False),
    ("code", 'from hermes_tools import web_search; web_search("test")', False),
    ("code", 'with open("D:/myagent/workspace/out.md", "w") as f: f.write("x")', False),
    ("shell", 'D:\\myagent\\workspace\\write-guard\\t.py', False),
]

failures = []
for kind, text, expect_block in CASES:
    hit = handler._scan(kind, text)
    blocked = hit is not None
    status = "OK " if blocked == expect_block else "FAIL"
    if blocked != expect_block:
        failures.append((kind, text, expect_block, hit))
    print(f"[{status}] kind={kind:5s} expect_block={expect_block!s:5s} hit={hit!r:12s} :: {text[:70]}")

# on_pre_tool_call 集成：terminal 违规 → dict block；合法 → None
r1 = handler.on_pre_tool_call("terminal", {"command": 'curl -o /tmp/x.html https://x.com'})
r2 = handler.on_pre_tool_call("terminal", {"command": "echo hello"})
r3 = handler.on_pre_tool_call("unknown_tool", {"filePath": "C:\\Users\\guwh\\AppData\\Local\\Temp\\s.png"})
r4 = handler.on_pre_tool_call("unknown_tool", {"url": "https://example.com/a.png"})
ok1 = isinstance(r1, dict) and r1.get("action") == "block" and "write-guard" in r1.get("message", "")
ok2 = r2 is None
ok3 = isinstance(r3, dict) and r3.get("action") == "block"
ok4 = r4 is None
_hook_cases = [("hook-block-terminal", ok1), ("hook-pass-terminal", ok2),
               ("hook-fallback-unknown-block", ok3), ("hook-fallback-unknown-pass", ok4)]
HOOK_N = len(_hook_cases)          # 计数来源=列表本身（质量审查 #5 消魔数）
for name, ok in _hook_cases:
    print(f"[{'OK ' if ok else 'FAIL'}] hook: {name}")
    if not ok:
        failures.append(("hook", name, None, None))

print()
# =====================================================================
# write-guard 扩展测试：守卫 A（配置写保护）/ 守卫 B（记忆写保护）/
# 调度器（[C,A,B] 轮询）/ 守卫异常隔离（FR-14）/ 审批消息内容断言
# 设计文档第 7 章 TC-A-01~47、TC-B-01~06、TC-S-01~03、TC-E-01~05、TC-M-01~08
# 只读测试：纯内存函数调用 + 环境变量/cwd 保存恢复，无磁盘写入（NFR-03）
# =====================================================================
import os as _os
import logging as _logging

new_failures = []
_new_case_count = 0   # LOW-4：运行时自增（_rec 内），与实际断言数永远一致

# 默认回退 HERMES_HOME（DR-05，等同 handler._DEFAULT_HERMES_HOME）
_DEFAULT = r"D:\myagent\.hermes"
_CFG = r"D:\myagent\.hermes\config.yaml"
_CFG_PROFILE = r"D:\myagent\.hermes\profiles\developer\config.yaml"
_CFG_CLI = r"D:\myagent\.hermes\cli-config.yaml"
# 运行时拼接的系统临时目录引用（避免源文件出现临时目录字面量）
_TMP_REF = "/" + "tmp" + "/x.log"


def _rec(name, ok, detail=""):
    global _new_case_count
    _new_case_count += 1
    print(f"[{'OK ' if ok else 'FAIL'}] {name}" + (f" :: {detail}" if detail else ""))
    if not ok:
        new_failures.append((name, detail))


def _is_approve(res):
    return isinstance(res, dict) and res.get("action") == "approve"


def _is_block(res):
    return isinstance(res, dict) and res.get("action") == "block"


def _set_hermes_home(value):
    if value is None:
        _os.environ.pop("HERMES_HOME", None)
    else:
        _os.environ["HERMES_HOME"] = value


from contextlib import contextmanager


@contextmanager
def _stub_guard(guard_name, replacement):
    """按 __name__ 定位并临时替换 GUARDS 中的守卫（质量审查 #3：禁止硬索引
    ——守卫增删/排序变化时旧硬索引会悄悄把桩插错位置）。
    guard_name 是函数名字符串契约（重命名守卫 → 此处立即报错，可见可修）。"""
    idx = next(i for i, g in enumerate(handler.GUARDS)
               if getattr(g, "__name__", "") == guard_name)
    orig = handler.GUARDS[idx]
    handler.GUARDS[idx] = replacement
    try:
        yield
    finally:
        handler.GUARDS[idx] = orig


def _call(tool_name, args, hermes_home=None):
    """调用 on_pre_tool_call；hermes_home 默认 None（删除环境变量 → 回退默认值）。
    保存 → 修改 → finally 恢复（DR-16，用例间互不影响）。"""
    saved = _os.environ.get("HERMES_HOME")
    try:
        _set_hermes_home(hermes_home)
        return handler.on_pre_tool_call(tool_name, args)
    finally:
        _set_hermes_home(saved)


# ---------- A 项：写工具路径命中（AC-02） ----------
def run_a_basic():
    res = _call("write_file", {"path": _CFG})
    _rec("TC-A-01 write_file 根 config.yaml → block（直接截断）", _is_block(res))
    res = _call("write_file", {"path": _CFG_PROFILE})
    _rec("TC-A-02 write_file profiles 下 config.yaml → block（直接截断）", _is_block(res))
    res = _call("write_file", {"path": _CFG_CLI})
    _rec("TC-A-03 write_file cli-config.yaml → block（直接截断）", _is_block(res))
    res = _call("patch", {"path": _CFG})
    _rec("TC-A-04 patch 指向受保护文件 → block（直接截断）", _is_block(res))
    ok = _call("write_file", {"path": None}) is None
    ok = ok and _call("write_file", {"path": 123}) is None
    ok = ok and _call("write_file", {"path": "   "}) is None
    ok = ok and _call("write_file", {}) is None
    _rec("TC-A-05 path 非字符串/缺失/空白 → 放行（DR-26）", ok)


# ---------- A 项：路径等价类变体（AC-03 / FR-04） ----------
def run_a_variants():
    res = _call("write_file", {"path": r"D:\MYAGENT\.HERMES\CONFIG.YAML"})
    _rec("TC-A-06 大小写变体 → block", _is_block(res))
    res = _call("write_file", {"path": "D:/myagent/.hermes/config.yaml"})
    _rec("TC-A-07 正斜杠变体 → block", _is_block(res))
    res = _call("write_file", {"path": r"D:\myagent/.hermes\config.yaml"})
    _rec("TC-A-08 混合分隔符 → block", _is_block(res))
    res = _call("write_file", {"path": r"%HERMES_HOME%\config.yaml"}, hermes_home=_DEFAULT)
    _rec("TC-A-09 命令解释器环境变量引用 → block", _is_block(res))
    res = _call("write_file", {"path": "$HERMES_HOME/config.yaml"}, hermes_home=_DEFAULT)
    _rec("TC-A-10 脚本风格引用 → block", _is_block(res))
    res = _call("write_file", {"path": "${HERMES_HOME}\\config.yaml"}, hermes_home=_DEFAULT)
    _rec("TC-A-11 花括号引用 → block", _is_block(res))
    res = _call("write_file", {"path": r"$env:HERMES_HOME\config.yaml"}, hermes_home=_DEFAULT)
    _rec("TC-A-12 PowerShell 风格 → block", _is_block(res))
    res = _call("write_file", {"path": r"%UNDEFINED_HOME%\config.yaml"})
    _rec("TC-A-13 环境变量未定义 → 放行", res is None)
    saved_cwd = _os.getcwd
    try:
        _os.getcwd = lambda: r"D:\myagent\.hermes"
        res = _call("write_file", {"path": "config.yaml"})
        _rec("TC-A-14 相对路径（cwd 在受保护目录）→ block", _is_block(res))
    finally:
        _os.getcwd = saved_cwd
    res = _call("write_file", {"path": r"D:\myagent\.hermes\profiles\..\config.yaml"})
    _rec("TC-A-15 上级目录段 → block", _is_block(res))
    res = _call("write_file", {"path": r"D:\myagent\.hermes\.\config.yaml"})
    _rec("TC-A-16 点段 → block", _is_block(res))
    res = _call("terminal", {"command": "cd D:/myagent/.hermes && echo hi > config.yaml"})
    ok = _is_block(res)
    res = _call("terminal", {"command": "cd /d D:\\myagent\\.hermes && echo hi > config.yaml"})
    ok = ok and _is_block(res)
    _rec("TC-A-17 终端 cd 链 echo > config → block（B3）", ok)
    res = _call("write_file", {"path": '"' + _CFG + '"'})
    _rec("TC-A-18 引号包裹路径 → block", _is_block(res))


# ---------- A 项：terminal 写形态矩阵（AC-02 / FR-02③ / FR-03） ----------
def run_a_terminal():
    res = _call("terminal", {"command": "echo hi > " + _CFG})
    ok = _is_block(res)
    res = _call("terminal", {"command": "printf '%s' x > " + _CFG})
    ok = ok and _is_block(res)
    _rec("TC-A-19 输出重定向 > → block（B3，echo/printf 双形态均断言）", ok)
    res = _call("terminal", {"command": "echo hi >> " + _CFG})
    _rec("TC-A-20 追加 >> → block（B3）", _is_block(res))
    res = _call("terminal", {"command": "echo hi | tee " + _CFG})
    ok = _is_block(res)
    res = _call("terminal", {"command": "echo hi | tee -a " + _CFG})
    ok = ok and _is_block(res)
    _rec("TC-A-21 tee / tee -a → block（B3）", ok)
    res = _call("terminal", {"command": "cp src.txt " + _CFG})
    _rec("TC-A-22 cp 目标为受保护文件 → approve", _is_approve(res))
    res = _call("terminal", {"command": "sed -i 's/a/b/' " + _CFG})
    _rec("TC-A-23 sed -i 原位编辑 → block（B3）", _is_block(res))
    res = _call("terminal", {"command": "dd if=/dev/zero of=" + _CFG})
    _rec("TC-A-24 dd of= → block（B3）", _is_block(res))
    res = _call("terminal", {"command": "python -c \"open('" + _CFG + "','w').write('x')\""})
    _rec("TC-A-25 内嵌脚本写调用 → block（B3）", _is_block(res))
    res = _call("terminal", {"command": "cp " + _CFG + " backup.yaml"})
    _rec("TC-A-26 cp 源（读方向）→ 放行", res is None)
    res = _call("terminal", {"command": "grep x " + _CFG})
    ok = res is None
    res = _call("terminal", {"command": "cat " + _CFG})
    ok = ok and res is None
    res = _call("terminal", {"command": "type " + _CFG})
    ok = ok and res is None
    res = _call("terminal", {"command": "diff a " + _CFG})
    ok = ok and res is None
    _rec("TC-A-27 只读命令 → 放行", ok)
    res = _call("terminal", {"command": "cat < " + _CFG})
    _rec("TC-A-28 输入重定向 → 放行", res is None)
    res = _call("terminal", {"command": "env | grep config"})
    ok = res is None
    res = _call("terminal", {"command": "P='/d/myagent/.hermes/config.yaml'; echo ok"})
    ok = ok and res is None
    _rec("TC-A-29 无法判定形态 → 放行", ok)


# ---------- A 项：execute_code 写形态（AC-02 / FR-02④） ----------
def run_a_execute_code():
    res = _call("execute_code", {"code": "open('" + _CFG + "', 'w')"})
    ok = _is_block(res)
    res = _call("execute_code", {"code": "open('" + _CFG + "', 'wb')"})
    ok = ok and _is_block(res)
    res = _call("execute_code", {"code": "open('" + _CFG + "', 'a')"})
    ok = ok and _is_block(res)
    res = _call("execute_code", {"code": "with open('" + _CFG + "', 'w') as f: pass"})
    ok = ok and _is_block(res)
    _rec("TC-A-30 open 写/追加模式 → block（B3）", ok)
    res = _call("execute_code", {"code": "Path('" + _CFG + "').write_text('x')"})
    ok = _is_block(res)
    res = _call("execute_code", {"code": "Path('" + _CFG + "').write_bytes(b'x')"})
    ok = ok and _is_block(res)
    res = _call("execute_code", {"code": "Path('" + _CFG + "').touch()"})
    ok = ok and _is_block(res)
    _rec("TC-A-31 Path 写方法 → block（B3）", ok)
    res = _call("execute_code", {"code": "shutil.copy('src.txt', '" + _CFG + "')"})
    _rec("TC-A-32 shutil.copy 目标 → approve", _is_approve(res))
    res = _call("execute_code", {"code": "hermes_tools.write_file(path='" + _CFG + "')"})
    _rec("TC-A-33 代码内工具调用 → block（B3）", _is_block(res))
    res = _call("execute_code", {"code": "open('" + _CFG + "', 'r')"})
    ok = res is None
    res = _call("execute_code", {"code": "open('" + _CFG + "')"})
    ok = ok and res is None
    res = _call("execute_code", {"code": "Path('" + _CFG + "').read_text()"})
    ok = ok and res is None
    _rec("TC-A-34 读模式放行", ok)
    res = _call("execute_code", {"code": "os.remove('" + _CFG + "')"})
    ok = res is None
    res = _call("execute_code", {"code": "os.rename('a.txt', '" + _CFG + "')"})
    ok = ok and res is None
    res = _call("execute_code", {"code": "shutil.move('a.txt', '" + _CFG + "')"})
    ok = ok and res is None
    _rec("TC-A-35 路径级操作放行（OOS-09）", ok)
    res = _call("execute_code", {"code": "print('" + _CFG + "')"})
    _rec("TC-A-36 路径仅作字符串 → 放行", res is None)
    res = _call("execute_code", {"code": "open(var_path, 'w')"})
    _rec("TC-A-37 动态变量路径 → 放行", res is None)


# ---------- A 项：范围边界（FR-01 / FR-05 / OOS-02） ----------
def run_a_bounds():
    res = _call("write_file", {"path": r"D:\myagent\workspace\out.md"})
    _rec("TC-A-38 非保护路径 → 放行", res is None)
    res = _call("write_file", {"path": r"D:\myagent\.hermes\skills\x.md"})
    ok = res is None
    res = _call("write_file", {"path": r"D:\myagent\.hermes\memories\y.md"})
    ok = ok and res is None
    _rec("TC-A-39 HERMES_HOME 内非 config 文件 → 放行", ok)
    saved = _os.environ.get("HERMES_HOME")
    try:
        _set_hermes_home(None)
        res = handler.on_pre_tool_call("write_file", {"path": _CFG})
        _rec("TC-A-40 HERMES_HOME 未设置 → 回退默认值命中 block", _is_block(res))
    finally:
        _set_hermes_home(saved)
    saved = _os.environ.get("HERMES_HOME")
    try:
        _set_hermes_home(r"D:\other\home")
        res_new = handler.on_pre_tool_call("write_file", {"path": r"D:\other\home\config.yaml"})
        res_old = handler.on_pre_tool_call("write_file", {"path": _CFG})
        _rec("TC-A-41 HERMES_HOME 其他值 → 新目录命中/旧目录放行",
             _is_block(res_new) and res_old is None)
    finally:
        _set_hermes_home(saved)
    saved = _os.environ.get("HERMES_HOME")
    try:
        _set_hermes_home("")
        res = handler.on_pre_tool_call("write_file", {"path": _CFG})
        _rec("TC-A-42 HERMES_HOME 空串 → 回退默认值命中 block", _is_block(res))
    finally:
        _set_hermes_home(saved)


# ---------- A 项：DESIGN_FIX 增补用例（MED-2/MED-3/LOW-4/LOW-5） ----------
def run_a_designfix():
    esc_cfg = "D:\\\\myagent\\\\.hermes\\\\config.yaml"   # 转义字面量（每段双反斜杠）
    res = _call("execute_code", {"code": "open(\"" + esc_cfg + "\",\"w\")"})
    ok = _is_block(res)
    res = _call("terminal", {"command": "echo hi > \"" + esc_cfg + "\""})
    ok = ok and _is_block(res)
    _rec("TC-A-43 字符串转义字面量形态 → block（B3）", ok)
    res = _call("write_file", {"path": r"%hermes_home%\config.yaml"}, hermes_home=_DEFAULT)
    ok = _is_block(res)
    res = _call("write_file", {"path": "$HERMES_home/config.yaml"}, hermes_home=_DEFAULT)
    ok = ok and _is_block(res)
    res = _call("write_file", {"path": "${HERMES_home}\\config.yaml"}, hermes_home=_DEFAULT)
    ok = ok and _is_block(res)
    _rec("TC-A-44 环境变量引用大小写变体 → block", ok)
    res = _call("read_file", {"path": _CFG})
    _rec("TC-A-45 read_file → 显式放行", res is None)
    res = _call("terminal", {"command": "cp somefile D:/myagent/.hermes/"})
    # 边界收紧（sa-0 F-A7 / 2026-09-21）：原 DR-25 接受「cp 至目录 → 放行」，
    # 但 `cp evil.yaml <home>/` 正是绕过「cp 目标文件」检测的写法；按用户决策
    # （cp 是改配置的方法 → 弹审批）翻转为 approve。读方向（cat/ls 目录）不受影响。
    _rec("TC-A-46 复制至受保护目录 → approve（F-A7 边界收紧）", _is_approve(res))
    res = _call("write_file", {"path": r"%HERMES_HOME_XY%\config.yaml"})
    ok = res is None
    res = _call("write_file", {"path": "$HERMES_HOME_XY/config.yaml"})
    ok = ok and res is None
    _rec("TC-A-47 环境变量名边界负例 → 放行", ok)


# ---------- B 项（AC-05 / FR-07 / FR-08） ----------
def run_b():
    res = _call("hindsight_retain", {"content": "任意参数"})
    _rec("TC-B-01 hindsight_retain → approve", _is_approve(res))
    res = _call("context_notes", {"action": "add", "content": "x"})
    _rec("TC-B-02 context_notes → approve", _is_approve(res))
    res = _call("memory", {"action": "add", "content": "x"})
    _rec("TC-B-03 内置 memory 写工具 → approve", _is_approve(res))
    res = _call("hindsight_recall", {"query": "x"})
    _rec("TC-B-04 hindsight_recall → 放行", res is None)
    res = _call("hindsight_reflect", {"query": "x"})
    _rec("TC-B-05 hindsight_reflect → 放行", res is None)
    res = _call("session_search", {"query": "x"})
    _rec("TC-B-06 内置记忆查询工具 → 放行", res is None)


# ---------- C 项：读取方向工具无条件放行（REQ-C1-01，用户收敛 5 工具） ----------
def run_c_readtools():
    # 清单内 5 个核心读取工具：无条件放行，不扫描参数（None）
    res = _call("search_files", {"pattern": "x", "path": _TMP_REF})
    _rec("TC-C1-01 search_files → 无条件放行", res is None)
    res = _call("read_file", {"path": _TMP_REF + "/a.md"})
    _rec("TC-C1-02 read_file → 无条件放行", res is None)
    res = _call("web_search", {"query": _TMP_REF})
    _rec("TC-C1-03 web_search → 无条件放行", res is None)
    res = _call("hindsight_recall", {"query": _TMP_REF})
    _rec("TC-C1-04 hindsight_recall → 无条件放行", res is None)
    res = _call("hindsight_reflect", {"query": _TMP_REF})
    _rec("TC-C1-05 hindsight_reflect → 无条件放行", res is None)
    # 写方向工具：保持不变（命中即 block）
    res = _call("terminal", {"command": "curl -o " + _TMP_REF + " https://x.com"})
    _rec("TC-C1-06 terminal 写临时目录 → block（不变）",
         isinstance(res, dict) and res.get("action") == "block")
    res = _call("write_file", {"path": _TMP_REF})
    _rec("TC-C1-07 write_file 写临时目录 → block（不变）",
         isinstance(res, dict) and res.get("action") == "block")
    # 未知工具兜底：保持不变（命中即 block）
    res = _call("unknown_tool_xyz", {"filePath": _TMP_REF + "/a.png"})
    _rec("TC-C1-08 未知工具兜底扫描 → block（不变）",
         isinstance(res, dict) and res.get("action") == "block")
    # process_manage 不在清单（走查 F-1）：kill 动作含临时目录字样 → block
    res = _call("process_manage", {"action": "kill", "session_id": _TMP_REF + "/x"})
    _rec("TC-C1-09 process_manage kill 含临时目录字样 → block（F-1 修复）",
         isinstance(res, dict) and res.get("action") == "block")
    # 移出清单的工具（用户收敛）：一律走参数检查 → 含临时目录字样时 block
    # 注：web_extract 的 urls 参数是 list，兜底扫描只扫字符串值不深入容器
    # （既有限制，非本次改动引入），故用字符串参数形态的工具验证兜底。
    res = _call("skill_view", {"name": "x", "file_path": _TMP_REF})
    _rec("TC-C1-10 skill_view（移出清单）含临时目录字样 → block",
         isinstance(res, dict) and res.get("action") == "block")
    res = _call("kanban_show", {"task_id": "t1", "note": _TMP_REF})
    _rec("TC-C1-11 kanban_show（移出清单）含临时目录字样 → block",
         isinstance(res, dict) and res.get("action") == "block")
    res = _call("skills_list", {"category": _TMP_REF})
    _rec("TC-C1-12 skills_list（移出清单）含临时目录字样 → block",
         isinstance(res, dict) and res.get("action") == "block")
    # 对抗性走查 T2：B1/B4/B5 绕过路径补测（write_file 变体 → 必须 block）
    res = _call("write_file", {"path": "\\\\?\\D:/myagent/.hermes/config.yaml"})
    _rec("TC-A-56 verbatim 前缀 \\\\?\\ → block（B5）", _is_block(res))
    res = _call("write_file", {"path": "/d/myagent/.hermes/config.yaml"})
    _rec("TC-A-57 MSYS /d/ 形态 → block（B4）", _is_block(res))
    res = _call("write_file", {"path": "/cygdrive/d/myagent/.hermes/config.yaml"})
    _rec("TC-A-58 MSYS /cygdrive/d/ 形态 → block（B4）", _is_block(res))
    # 对抗性走查 B2 补测（用户决策「范围要扩大」）：非 config 子串配置文件 → block
    res = _call("write_file", {"path": r"D:\myagent\.hermes\profile.yaml"})
    _rec("TC-A-59 profile.yaml → block（B2 扩大）", _is_block(res))
    res = _call("write_file", {"path": r"D:\myagent\.hermes\settings.yaml"})
    _rec("TC-A-60 settings.yaml → block（B2 扩大）", _is_block(res))
    res = _call("write_file", {"path": r"D:\myagent\.hermes\.env"})
    _rec("TC-A-61 .env → block（B2 扩大）", _is_block(res))
    res = _call("write_file", {"path": r"D:\myagent\.hermes\tui-theme-boot.json"})
    _rec("TC-A-62 .json 配置 → block（B2 扩大）", _is_block(res))
    # B2 负例：非配置文件（.md/.py）仍放行
    res = _call("write_file", {"path": r"D:\myagent\.hermes\skills\guide.md"})
    _rec("TC-A-63 skills/*.md 非配置 → 放行（B2 负例）", res is None)
    # 用户决策 2026-09-21（L4 确认）：「改名和复制不拦截」——
    # shutil.move / os.rename / os.replace 目标为配置文件 → 保持放行
    res = _call("execute_code", {"code": "shutil.move('D:/myagent/.hermes/scr.md', 'D:/myagent/.hermes/config.yaml')"})
    _rec("TC-A-64 move 改名覆盖配置 → 放行（L4 用户决策）", res is None)
    res = _call("execute_code", {"code": "os.rename('D:/myagent/.hermes/scr.md', 'D:/myagent/.hermes/profile.yaml')"})
    _rec("TC-A-65 rename 改名覆盖配置 → 放行（L4 用户决策）", res is None)
    res = _call("execute_code", {"code": "os.replace('D:/myagent/.hermes/scr.md', 'D:/myagent/.hermes/settings.yaml')"})
    _rec("TC-A-66 replace 改名覆盖配置 → 放行（L4 用户决策）", res is None)
    # TC-C1-13 不变量断言（走查 F-3）：清单与写方向/记忆写/配置写工具集无交集，
    # 且不含已废弃条目。若未来误把写工具加回清单，此断言立即失败（防静默回归）。
    # 安全不变量（红线，必须恒真）：读清单与写方向/记忆写工具集无交集，
    # 且不含已废弃条目（误并入写能力的读工具会静默旁路 A/B/C 守卫）。
    _inv_ok = (
        handler._READ_TOOLS.isdisjoint(handler._TOOL_ARG_MAP)
        and handler._READ_TOOLS.isdisjoint(handler._MEMORY_WRITE_TOOLS)
        and not ({"process_manage", "web_extract", "skill_view", "session_search"} & handler._READ_TOOLS)
    )
    _rec("TC-C1-13 清单安全不变量（与写工具零交集、无废弃条目）", _inv_ok)
    # 清单快照（变更提醒，非安全红线）：5 项清单是用户决策 2026-09-21
    # 「只写几个就行了」的定案。新增合法读工具时本断言失败属**预期提醒**：
    # 人工确认该读工具确实纯读后，同步更新 handler._READ_TOOLS 与本快照。
    _snap_ok = handler._READ_TOOLS == {"read_file", "search_files", "web_search",
                                       "hindsight_recall", "hindsight_reflect"}
    _rec("TC-C1-14 清单快照=定案 5 项（变更需人工确认）", _snap_ok)


# ---------- 调度器（AC-09 / AC-07 / FR-12 / FR-13） ----------

def run_gateway_cmd():
    """守卫 D：hermes gateway restart/run/start 禁令（用户决策 2026-09-21）。"""
    global _new_case_count
    # 1. 直写三动词 → block
    res = _call("terminal", {"command": "hermes gateway restart"})
    _rec("TC-D-01 hermes gateway restart → block", _is_block(res))
    res = _call("terminal", {"command": "hermes gateway run"})
    _rec("TC-D-02 hermes gateway run → block", _is_block(res))
    res = _call("terminal", {"command": "hermes gateway start"})
    _rec("TC-D-03 hermes gateway start → block", _is_block(res))
    # 2. 全局 flag / 路径前缀 / 大小写形态 → block
    res = _call("terminal", {"command": "hermes -p dev gateway restart"})
    _rec("TC-D-04 全局 flag 形态 → block", _is_block(res))
    res = _call("terminal", {"command": "D:/proj/venv/Scripts/hermes.exe gateway start"})
    _rec("TC-D-05 完整路径 exe 形态 → block", _is_block(res))
    res = _call("terminal", {"command": "HERMES Gateway RESTART"})
    _rec("TC-D-06 大小写混写 → block", _is_block(res))
    # 3. 与禁令无关的形态 → 放行（低误拦边界）
    res = _call("terminal", {"command": "hermes gateway status"})
    _rec("TC-D-07 hermes gateway status → 放行", res is None)
    res = _call("terminal", {"command": "hermes gateway stop"})
    _rec("TC-D-08 hermes gateway stop → 放行（不在本次禁令内）", res is None)
    res = _call("terminal", {"command": "hermes gateway --help"})
    _rec("TC-D-09 hermes gateway --help → 放行", res is None)
    # 设计决策：禁令按命令文本匹配，提及禁令动词同样 block（宁可多拦，
    # 用户改写法即可）——与 C 的"纯文本提及放行"边界不同，属有意收紧。
    res = _call("terminal", {"command": "grep -r 'hermes gateway restart' docs/"})
    _rec("TC-D-10 参数文本提及 → block（按命令文本匹配，有意收紧）", _is_block(res))
    res = _call("terminal", {"command": "echo hello; hermes gateway restart"})
    _rec("TC-D-11 组合段内嵌禁令命令 → block", _is_block(res))
    # 4. execute_code 面 → block
    res = _call("execute_code", {"code": "terminal('hermes gateway restart')"})
    _rec("TC-D-12 execute_code 内嵌禁令命令 → block", _is_block(res))
    # 5. 消息文案 = handler 常量（用户指定文案，唯一权威定义在 handler 侧）
    res = _call("terminal", {"command": "hermes gateway run"})
    ok = (res is not None and isinstance(res, dict) and res.get("action") == "block"
          and res.get("message", "") == handler._GATEWAY_BANNED_MESSAGE)
    _rec("TC-D-13 block 消息 = handler._GATEWAY_BANNED_MESSAGE", ok)
    # 6. 非命令工具不受 D 影响（read_file 路径含禁令字样 → 放行）
    res = _call("read_file", {"path": "D:/myagent/workspace/hermes gateway restart.txt"})
    _rec("TC-D-14 读文件路径含禁令字样 → 放行", res is None)



def run_sec_bypass():
    """sa-0 对抗安全走查修复回归（F-A1~A7 + C-cwd + 反缴械）。"""
    global _new_case_count
    S = chr(92)                                    # 单个反斜杠
    H = "D:" + S + "myagent" + S + ".hermes"
    CFG = H + S + "config.yaml"
    WS = "D:" + S + "myagent" + S + "workspace"

    # F-A1：字符串前缀 r/b/f 不得击穿 open 族正则
    for tag, code in [
        ("r", "open(r'" + CFG + "', 'w').write('x')"),
        ("R", "open(R'" + CFG + "', 'w')"),
        ("f", "open(f'" + CFG + "', 'a')"),
        ("rb", "open(rb'" + CFG + "', 'wb')"),
        ("br", "open(br'" + CFG + "', 'wb')"),
    ]:
        res = _call("execute_code", {"code": code})
        _rec("TC-E11 open 前缀 " + tag + " 写配置 → block（F-A1）", _is_block(res))
    res = _call("execute_code", {"code": "Path(r'" + CFG + "').write_text('x')"})
    _rec("TC-E12 Path(r'') write_text → block（F-A1）", _is_block(res))
    res = _call("execute_code", {"code": "Path(r'" + CFG + "').open('w')"})
    _rec("TC-E13 Path(r'').open → block（F-A1）", _is_block(res))
    res = _call("execute_code", {"code": "os.open(r'" + CFG + "', os.O_WRONLY)"})
    _rec("TC-E14 os.open(r'') → block（F-A1）", _is_block(res))
    res = _call("execute_code", {"code": "shutil.copy(r'a.yaml', r'" + CFG + "')"})
    _rec("TC-E15 shutil.copy(r'') 目标 → approve（F-A1 等效 cp）", _is_approve(res))
    res = _call("execute_code", {"code": "write_file(path=r'" + CFG + "', content='x')"})
    _rec("TC-E16 内嵌 write_file(r'') → block（F-A1）", _is_block(res))
    res = _call("execute_code", {"code": "open(r'" + CFG + "', 'rb').read()"})
    _rec("TC-E17 open(r'', 'rb') 只读 → 放行（F-A1 负例）", res is None)

    # F-A2：execute_code 内嵌 shell 不得旁路 terminal 判定
    N = chr(10)
    res = _call("execute_code", {"code": "import os" + N + "os.system('echo evil> " + CFG + "')"})
    _rec("TC-E20 os.system 写配置 → block（F-A2）", _is_block(res))
    res = _call("execute_code", {"code": "import os" + N + "os.popen('cp a.yaml " + CFG + "')"})
    _rec("TC-E21 os.popen cp → approve（F-A2 等效 cp）", _is_approve(res))
    res = _call("execute_code", {"code": "import subprocess" + N + "subprocess.run('tee " + CFG + "', shell=True)"})
    _rec("TC-E22 subprocess.run tee → block（F-A2）", _is_block(res))
    res = _call("execute_code", {"code": "import subprocess" + N + "subprocess.run(['cp', 'a.yaml', '" + CFG + "'])"})
    _rec("TC-E23 subprocess list 形态 cp 目标 → approve（F-A2）", _is_approve(res))
    res = _call("execute_code", {"code": "import subprocess" + N + "subprocess.run('cat x > " + CFG + "', shell=True)"})
    _rec("TC-E24 subprocess 重定向 → block（F-A2）", _is_block(res))
    res = _call("execute_code", {"code": "import subprocess" + N + "subprocess.run(['cat', '" + CFG + "'])"})
    _rec("TC-E25 subprocess 只读 cat → 放行（F-A2 负例）", res is None)
    res = _call("execute_code", {"code": "import os" + N + "os.system('echo hi > " + WS + S + "a.txt')"})
    _rec("TC-E26 os.system 写非配置 → 放行（F-A2 负例）", res is None)

    # F-A3：反缴械——守卫自身源码与插件清单受保护
    PG = H + S + "plugins" + S
    res = _call("write_file", {"path": PG + "write-guard" + S + "handler.py"})
    _rec("TC-E30 write_file 改守卫源码 → block（F-A3 反缴械）", _is_block(res))
    res = _call("write_file", {"path": PG + "write-guard" + S + "plugin.yaml"})
    _rec("TC-E31 write_file 改插件清单 → block（F-A3）", _is_block(res))
    res = _call("patch", {"path": PG + "x" + S + "init.py"})
    _rec("TC-E32 patch 改他插件源码 → block（F-A3）", _is_block(res))
    res = _call("write_file", {"path": PG + "x" + S + "README.md"})
    _rec("TC-E33 plugins 下 .md 非代码 → 放行（F-A3 负例）", res is None)
    res = _call("write_file", {"path": WS + S + "write-guard" + S + "handler.py"})
    _rec("TC-E34 工作区插件源码（开发位）→ 放行（F-A3 负例）", res is None)

    # F-A4：sed -i 带后缀 / 长形态
    res = _call("terminal", {"command": "sed -i.bak 's/a/b/' " + CFG})
    _rec("TC-E40 sed -i.bak → block（F-A4）", _is_block(res))
    res = _call("terminal", {"command": "sed --in-place=.bak 's/a/b/' " + CFG})
    _rec("TC-E41 sed --in-place=.bak → block（F-A4）", _is_block(res))
    res = _call("terminal", {"command": "perl -pi -e 's/a/b/' " + CFG})
    _rec("TC-E42 perl -pi → block（F-A4）", _is_block(res))
    res = _call("terminal", {"command": "sed -n '1p' " + CFG})
    _rec("TC-E43 sed -n 只读 → 放行（F-A4 负例）", res is None)

    # F-A5/F-A6：truncate 与 PowerShell 写 cmdlet
    res = _call("terminal", {"command": "truncate -s 0 " + CFG})
    _rec("TC-E50 truncate -s 0 → block（F-A5）", _is_block(res))
    res = _call("terminal", {"command": "pwsh -c Set-Content -Path " + CFG + " -Value evil"})
    _rec("TC-E51 pwsh Set-Content → block（F-A6）", _is_block(res))
    res = _call("terminal", {"command": "powershell Add-Content " + CFG + " 'x'"})
    _rec("TC-E52 powershell Add-Content → block（F-A6）", _is_block(res))
    res = _call("terminal", {"command": "pwsh -c Get-Content -Path " + CFG})
    _rec("TC-E53 Get-Content 只读 → 放行（F-A6 负例）", res is None)

    # F-A7：cp 目标为受保护目录本身
    res = _call("terminal", {"command": "cp x.yaml D:/myagent/.hermes/"})
    _rec("TC-E60 cp 目标为 HERMES_HOME 目录 → approve（F-A7）", _is_approve(res))
    res = _call("terminal", {"command": "cp -t D:/myagent/.hermes x.yaml"})
    _rec("TC-E61 cp -t HERMES_HOME → approve（F-A7）", _is_approve(res))

    # C-cwd：terminal cwd 参数不得旁路临时目录扫描
    res = _call("terminal", {"command": "ls", "cwd": "/" + "tmp"})
    _rec("TC-E70 terminal 幻觉 cwd 指临时目录 → block（F-6 防御纵深超集）",
         _is_block(res))
    res = _call("terminal", {"command": "ls", "cwd": "D:/myagent/workspace"})
    _rec("TC-E71 terminal cwd 工作区 → 放行（C-cwd 负例）", res is None)

    # F-A2 递归链：terminal→python→os.system 穿透判定 + 有界终止
    q = chr(34)
    deep = "python -c " + q + "import os;os.system('tee " + CFG + "')" + q
    res = _call("terminal", {"command": deep})
    _rec("TC-E80 三层嵌套 shell 写配置 → 命中判定（F-A2 递归链）",
         _is_block(res) or _is_approve(res))
    try:
        ok_depth = _call("terminal", {"command": "echo normal"}) is None
    except RecursionError:
        ok_depth = False
    _rec("TC-E81 判定链有界终止（无 RecursionError）", ok_depth)




def run_m_fixes():
    """round2 复审（sa-1 23:49 报告）M-1/M-2/M-3 修复回归。"""
    global _new_case_count
    S = chr(92)
    CFG = "D:" + S + "myagent" + S + ".hermes" + S + "config.yaml"
    q = chr(34)

    # M-1：terminal 内嵌 shell 载体（引号体是完整 shell 命令）
    res = _call("terminal", {"command": "bash -c " + q + "echo x > " + CFG + q})
    _rec("TC-M101 bash -c 内嵌重定向 → block（M-1）", _is_block(res))
    res = _call("terminal", {"command": "pwsh -NoProfile -Command " + q + "echo x > " + CFG + q})
    _rec("TC-M102 pwsh -NoProfile -Command → block（M-1）", _is_block(res))
    res = _call("terminal", {"command": "cmd /c " + q + "echo x > " + CFG + q})
    _rec("TC-M103 cmd /c 内嵌重定向 → block（M-1）", _is_block(res))
    res = _call("terminal", {"command": "sh -c " + q + "cp a.yaml " + CFG + q})
    _rec("TC-M104 sh -c 内嵌 cp → approve（M-1 处置分流保持）", _is_approve(res))
    res = _call("terminal", {"command": "bash -c " + q + "cat " + CFG + q})
    _rec("TC-M105 bash -c 只读 cat → 放行（M-1 负例）", res is None)
    res = _call("terminal", {"command": "echo " + q + "config.yaml: backup" + q + " >> note.txt"})
    _rec("TC-M106 echo 引号体非 shell 载体（echo 不在解释器清单）→ 放行（负例）", res is None)

    # M-2：open 附加参数 / 命名 mode 形态
    res = _call("execute_code", {"code": "open('" + CFG + "', 'w', encoding='utf-8')"})
    _rec("TC-M110 open 带 encoding 追加参 → block（M-2）", _is_block(res))
    res = _call("execute_code", {"code": "open('" + CFG + "', mode='w')"})
    _rec("TC-M111 open mode= 命名参 → block（M-2）", _is_block(res))
    res = _call("execute_code", {"code": "open('" + CFG + "', 'r', encoding='utf-8')"})
    _rec("TC-M112 open 'r' + encoding → 放行（M-2 负例）", res is None)

    # M-3：显式 workdir 作为相对路径判定基准
    res = _call("terminal", {"command": "echo x > config.yaml",
                             "workdir": "D:/myagent/.hermes"})
    _rec("TC-M120 workdir=HERMES_HOME + 相对写 → block（M-3）", _is_block(res))
    res = _call("terminal", {"command": "echo x > config.yaml",
                             "workdir": "D:/myagent/workspace"})
    _rec("TC-M121 workdir=workspace 相对写 → 放行（M-3 负例）", res is None)
    res = _call("terminal", {"command": "cp k.yaml config.yaml",
                             "workdir": "D:/myagent/.hermes"})
    _rec("TC-M122 workdir + 相对 cp 目标 → approve（M-3 分流保持）", _is_approve(res))


def run_x_invariants():
    """结构不变量与引号感知分段回归（sa-1 R-1/S-4 复审后锁定）。"""
    global _new_case_count
    S = chr(92)
    CFG = "D:" + S + "myagent" + S + ".hermes" + S + "config.yaml"

    # R-1：引号内的 ; 与 | 不是分隔符（漏判方向缺陷的回归）
    res = _call("terminal", {"command": "sed -i 's/a;b/x;' " + CFG})
    _rec("TC-X-01 sed -i 引号内含 ; → block（R-1）", _is_block(res))
    res = _call("terminal", {"command": "sed -i \"s/x/y/\" " + CFG})
    _rec("TC-X-02 sed -i 双引号形态 → block（R-1）", _is_block(res))
    res = _call("terminal", {"command": "echo 'a;b' > " + CFG})
    _rec("TC-X-03 引号内含 ; 的重定向 → block（R-1）", _is_block(res))
    res = _call("terminal", {"command": "cat \"x;y\" | tee " + CFG})
    _rec("TC-X-04 管道引号内 ; + tee → block（R-1）", _is_block(res))
    # 负例：引号外的正常分段仍工作
    res = _call("terminal", {"command": "sed -n '1p' " + CFG + "; echo done"})
    _rec("TC-X-05 引号外 ; 分段只读 → 放行（R-1 负例）", res is None)
    # 引号不配平 → 不切分、整体兜底（保守不误伤也不假放行错误语义）
    res = _call("terminal", {"command": "echo x > " + CFG + " \"unbalanced"})
    _rec("TC-X-06 引号不配平的重定向 → block（整体兜底）", _is_block(res))
    # _split_shell 单元语义（返回 strip 后片段，空段滤除）
    sp = handler._split_shell("a 'b;c' && d", ("&&", "||", ";"))
    _rec("TC-X-07 _split_shell 引号内 ; 不切", sp == ["a 'b;c'", "d"])
    sp2 = handler._split_shell("a || b | c", ("||", "|"))
    _rec("TC-X-08 _split_shell || 先于 | 消耗", sp2 == ["a", "b", "c"])
    sp3 = handler._split_shell("a 'unclosed; b", (";",))
    _rec("TC-X-09 不配平拒绝切分（整体返回）", sp3 == ["a 'unclosed; b"])

    # S-4：覆盖面分叉不变量（A 扫描集 ⊆ C 参数映射键集）
    _rec("TC-X-10 A 扫描集 ⊆ C 映射键集（S-4 不变量）",
         set(handler._CONFIG_SCAN_TOOLS).issubset(set(handler._TOOL_ARG_MAP.keys())))

    # S-5：未知工具显式兜底（不把任意参数当 code 误判）
    res = _call("terminal", {"command": "uptime"})
    _rec("TC-X-11 无害命令放行（dispatch 显式化负例）", res is None)



def run_r3_fixes():
    """round3 复审修复回归（N-2 workdir / N-3 三引号 / N-5 调用形态 /
    N-6 rsync / N-4 递归基准 / H-1 目录目标）。"""
    global _new_case_count
    S = chr(92)
    HOME = "D:" + S + "myagent" + S + ".hermes"
    CFG = HOME + S + "config.yaml"
    q = chr(34)
    tq = chr(39) * 3
    # N-2：平台真实参数名 workdir（C 面 + A 面基准）
    res = _call("terminal", {"command": "touch ok", "workdir": "D:" + S + "tmp"})
    _rec("TC-R3-01 terminal workdir 指临时目录 → block（N-2/C）", _is_block(res))
    res = _call("terminal", {"command": "echo hi > config.yaml", "workdir": "D:/myagent/.hermes"})
    _rec("TC-R3-02 workdir=HOME + 相对重定向 → block（N-2/A）", _is_block(res))
    res = _call("terminal", {"command": "echo hi > config.yaml", "workdir": "D:/myagent/workspace"})
    _rec("TC-R3-03 workdir=workspace 相对写 → 放行（N-2 负例）", res is None)
    # N-4：内嵌递归继承 cwd 基准
    res = _call("terminal", {"command": "bash -c " + q + "echo x > config.yaml" + q,
                             "workdir": "D:/myagent/.hermes"})
    _rec("TC-R3-04 bash -c 相对写 + workdir → block（N-4）", _is_block(res))
    # N-1：getstatusoutput / from-import 裸词
    res = _call("execute_code", {"code": "import os" + chr(10) + "os.getstatusoutput('echo x > " + CFG + "')"})
    _rec("TC-R3-05 os.getstatusoutput 写配置 → block（N-1）", _is_block(res))
    res = _call("execute_code", {"code": "from subprocess import run" + chr(10) + "run('echo x > " + CFG + "', shell=True)"})
    _rec("TC-R3-06 from-import 裸 run 写配置 → block（N-1）", _is_block(res))
    res = _call("execute_code", {"code": "def run(x): return x" + chr(10) + "run('echo x > " + CFG + "')"})
    _rec("TC-R3-07 业务函数 run() 不误拦（N-1 from-import 门）", res is None)
    # N-3：三引号折叠
    res = _call("execute_code", {"code": "open(" + tq + CFG + tq + ", 'w')"})
    _rec("TC-R3-08 open(三引号) 写配置 → block（N-3）", _is_block(res))
    res = _call("execute_code", {"code": "Path(" + tq + CFG + tq + ").write_text('x')"})
    _rec("TC-R3-09 Path(三引号).write_text → block（N-3）", _is_block(res))
    # N-5：位置参 / dict 形工具调用
    res = _call("execute_code", {"code": "write_file('" + CFG + "', 'evil')"})
    _rec("TC-R3-10 write_file 位置参 → block（N-5）", _is_block(res))
    res = _call("execute_code", {"code": "call({'path': '" + CFG + "', 'content': 'x'})"})
    _rec("TC-R3-11 dict 形 path 键 → block（N-5）", _is_block(res))
    res = _call("execute_code", {"code": "cfg = {'path': 'a.md'}"})
    _rec("TC-R3-12 无关 dict path 不误拦（N-5 负例）", res is None)
    # N-6：rsync 复制语义
    res = _call("terminal", {"command": "rsync a.yaml D:/myagent/.hermes/config.yaml"})
    _rec("TC-R3-13 rsync 写受保护 → approve（N-6 复制族）", _is_approve(res))
    res = _call("terminal", {"command": "rsync D:/myagent/.hermes/config.yaml backup/"})
    _rec("TC-R3-14 rsync 读受保护为源 → 放行（N-6 负例）", res is None)
    # H-1：cp 目标为 home 内子目录
    res = _call("terminal", {"command": "cp evil.py D:/myagent/.hermes/plugins/write-guard/"})
    _rec("TC-R3-15 cp 至插件子目录 → approve（H-1）", _is_approve(res))
    res = _call("terminal", {"command": "cat D:/myagent/.hermes/plugins/write-guard/"})
    _rec("TC-R3-16 cat 插件子目录 → 放行（H-1 负例）", res is None)


def run_r5_fixes():
    """round5 复审修复回归（双路 finding：F-1/F-2/F-3/F-5/F-7/R4-1/F-4 边界）。"""
    GUARD = "D:/myagent/.hermes/plugins/write-guard"
    CFG = "D:/myagent/.hermes/config.yaml"
    # F-1（HIGH）：守卫目录复制目标——无尾分隔符同义形态不再旁路
    res = _call("terminal", {"command": "cp evil.py " + GUARD})
    _rec("TC-R5-01 cp 守卫目录无斜杠 → approve（F-1）", _is_approve(res))
    res = _call("terminal", {"command": 'cp evil.py "' + GUARD + '"'})
    _rec("TC-R5-02 cp 守卫目录引号包裹 → approve（F-1）", _is_approve(res))
    res = _call("terminal", {"command": "cp -t " + GUARD + " evil.py"})
    _rec("TC-R5-03 cp -t 守卫目录无斜杠 → approve（F-1）", _is_approve(res))
    res = _call("terminal", {"command": "cat " + GUARD + "/plugin.yaml"})
    _rec("TC-R5-04 cat 守卫目录文件 → 放行（F-1 负例：读不拦）", res is None)
    # F-2：workdir 相对形态按平台语义绝对化（显式锚定进程 cwd 基准，
    # 不依赖 runner 实际 cwd——判定语义：workdir 相对会话 cwd=进程 cwd 常态）
    saved_cwd = _os.getcwd
    _os.getcwd = lambda: r"D:\myagent\workspace"
    try:
        res = _call("terminal", {"command": "echo x > config.yaml",
                                 "workdir": "../.hermes"})
    finally:
        _os.getcwd = saved_cwd
    _rec("TC-R5-05 workdir=../.hermes 相对写 → block（F-2）", _is_block(res))
    # F-3：from-import 门别名/star/多行括号形
    res = _call("execute_code", {"code": "import subprocess as sp\n"
                                        "sp.run('echo x > " + CFG + "', shell=True)"})
    _rec("TC-R5-06 import subprocess as sp 别名 → block（F-3）", _is_block(res))
    res = _call("execute_code", {"code": "from subprocess import run as r\n"
                                        "r('echo x > " + CFG + "', shell=True)"})
    _rec("TC-R5-07 from import run as r 别名 → block（F-3）", _is_block(res))
    res = _call("execute_code", {"code": "from subprocess import *\n"
                                        "run('echo x > " + CFG + "', shell=True)"})
    _rec("TC-R5-08 from import * → block（F-3）", _is_block(res))
    res = _call("execute_code", {"code": "from subprocess import (\n    run,\n)\n"
                                        "run('echo x > " + CFG + "', shell=True)"})
    _rec("TC-R5-09 多行括号 import → block（F-3）", _is_block(res))
    res = _call("execute_code", {"code": "def run():\n    pass\nrun()"})
    _rec("TC-R5-10 业务 run() 无 import → 放行（F-3 负例零误拦）", res is None)
    # F-5：大写命令词（与 _PS_WRITE_RE 同族对齐 IGNORECASE）
    res = _call("terminal", {"command": "SED -i 's/a/b/' " + CFG})
    _rec("TC-R5-11 SED 大写 -i → block（F-5）", _is_block(res))
    res = _call("terminal", {"command": "DD of=" + CFG})
    _rec("TC-R5-12 DD 大写 of= → block（F-5）", _is_block(res))
    res = _call("terminal", {"command": "PERL -pi -e 's/a/b/' " + CFG})
    _rec("TC-R5-13 PERL 大写 -pi → block（F-5）", _is_block(res))
    # R4-1：rsync -t 是 preserve-times，不得按 cp -t 目标语义过拦
    res = _call("terminal", {"command": "rsync -t " + CFG + " backup/"})
    _rec("TC-R5-14 rsync -t 纯读方向 → 放行（R4-1 误拦修复）", res is None)
    # F-4：robocopy 假并入撤回——三参定向覆写为声明边界（锁 PASS 防语义漂移）
    res = _call("terminal", {"command": "robocopy src D:/myagent/.hermes config.yaml"})
    _rec("TC-R5-15 robocopy 三参 → 放行（F-4 声明边界锁定）", res is None)
    # F-7：args 非 dict 不再三守卫连抛整链放行（收敛为空参数走链）
    res = handler.on_pre_tool_call("terminal", None, "t")
    _rec("TC-R5-16 args=None 不抛异常按空参放行（F-7）", res is None)


def run_r6_fixes():
    """round6 复审修复回归（sa-0 D1/C3/C4 + sa-1 F-Q4）。"""
    GUARD = "D:/myagent/.hermes/plugins/write-guard"
    PGUARD = "D:/myagent/.hermes/profiles/architect/plugins/write-guard"
    CFG = "D:/myagent/.hermes/config.yaml"
    # D1：profile 镜像守卫目录纳入反缴械保护面
    res = _call("write_file", {"path": PGUARD + "/handler.py", "content": "x"})
    _rec("TC-R6-01 write_file 镜像目录 handler.py → block（D1）", _is_block(res))
    res = _call("write_file", {"path": PGUARD + "/plugin.yaml", "content": "x"})
    _rec("TC-R6-02 write_file 镜像目录 plugin.yaml → block（D1）", _is_block(res))
    res = _call("terminal", {"command": "cp evil.py " + PGUARD})
    _rec("TC-R6-03 cp 镜像守卫目录无斜杠 → approve（D1）", _is_approve(res))
    res = _call("terminal", {"command": "cat " + PGUARD + "/plugin.yaml"})
    _rec("TC-R6-04 cat 镜像目录文件 → 放行（D1 负例）", res is None)
    # C3：--target-directory 长形/=粘连/短形簇
    res = _call("terminal", {"command": "cp --target-directory " + GUARD + " x.txt"})
    _rec("TC-R6-05 cp --target-directory 守卫目录 → approve（C3）", _is_approve(res))
    res = _call("terminal", {"command": "cp --target-directory=" + GUARD + " x.txt"})
    _rec("TC-R6-06 cp --target-directory=粘连 → approve（C3）", _is_approve(res))
    res = _call("terminal", {"command": "cp -T " + GUARD + " x.txt"})
    _rec("TC-R6-07 cp -T（非目标标志）守卫目录在源位 → 放行（C3 负例不误扩）",
         res is None)
    # C4：home 内目录无尾分隔符末位（与带斜杠名实一致）
    res = _call("terminal", {"command": "cp x.yaml D:/myagent/.hermes/profiles/developer"})
    _rec("TC-R6-08 cp 末位=home 内目录无斜杠 → approve（C4）", _is_approve(res))
    res = _call("terminal", {"command": "cat D:/myagent/.hermes/profiles/developer"})
    _rec("TC-R6-09 cat home 内目录 → 放行（C4 负例）", res is None)
    res = _call("terminal", {"command": "mv x D:/myagent/.hermes/profiles/developer"})
    _rec("TC-R6-10 mv 同形 → 放行（C4 负例：改名族不拦）", res is None)
    # F-Q4：subprocess.getstatusoutput 限定形
    res = _call("execute_code", {"code": "import subprocess\n"
                        "subprocess.getstatusoutput('echo x > " + CFG + "')"})
    _rec("TC-R6-11 subprocess.getstatusoutput 限定形 → block（F-Q4）", _is_block(res))


def run_r7_fixes():
    """round7 复审修复回归（sa-0 D 卷 NL 旁路 + Q-6-1 粘连/引号选项形）。"""
    NL, CR, BS, Q = chr(10), chr(13), chr(92), chr(34)
    GUARD = "D:/myagent/.hermes/plugins/write-guard"
    PGUARD = "D:/myagent/.hermes/profiles/architect/plugins/write-guard"
    CFG = "D:/myagent/.hermes/config.yaml"
    # NL（round6 sa-0 D 卷 HIGH）：换行=命令分隔符必须参与分段
    res = _call("terminal", {"command": "ls" + NL + "cp evil " + GUARD})
    _rec("TC-R7-01 换行后 cp 守卫目录 → approve（NL 旁路封堵）", _is_approve(res))
    res = _call("terminal", {"command": "ls" + NL + "cp evil " + PGUARD})
    _rec("TC-R7-02 换行后 cp 镜像守卫目录 → approve（NL+D1 组合）", _is_approve(res))
    res = _call("terminal", {"command": "ls" + NL + "truncate -s 0 " + CFG})
    _rec("TC-R7-03 换行后 truncate 配置 → block（NL）", _is_block(res))
    res = _call("terminal", {"command": "echo hi" + CR + NL + "cp evil " + GUARD})
    _rec("TC-R7-04 CRLF 换行 cp 守卫目录 → approve（NL）", _is_approve(res))
    res = _call("terminal", {"command": "cp evil " + BS + NL + GUARD})
    _rec("TC-R7-05 反斜杠续行 cp 守卫目录 → approve（NL 粘连归一）", _is_approve(res))
    res = _call("terminal", {"command": "ls" + NL + "cat " + GUARD + "/plugin.yaml"})
    _rec("TC-R7-06 换行后读守卫目录文件 → 放行（NL 负例）", res is None)
    res = _call("terminal", {"command": "ls" + NL + "echo x > D:/myagent/workspace/a.txt"})
    _rec("TC-R7-07 换行后 workspace 写 → 放行（NL 负例）", res is None)
    # Q-6-1：粘连短形与引号选项形
    res = _call("terminal", {"command": "cp -t" + GUARD + " evil"})
    _rec("TC-R7-08 cp -t<守卫目录> 粘连 → approve（Q-6-1）", _is_approve(res))
    res = _call("terminal", {"command": "cp -t=" + GUARD + " evil"})
    _rec("TC-R7-09 cp -t=<守卫目录> 等号粘连 → approve（Q-6-1）", _is_approve(res))
    res = _call("terminal", {"command": "cp '-t' " + GUARD + " evil"})
    _rec("TC-R7-10 cp '-t' 引号选项形 → approve（Q-6-1）", _is_approve(res))
    res = _call("terminal", {"command": "cp -tr " + GUARD + " x"})
    _rec("TC-R7-11 cp -tr GUARD x（getopt 余部=目标 r、GUARD 源位）→ 放行（负例）",
         res is None)
    res = _call("terminal", {"command": "cp '-t' workspace" + BS + "x workspace" + BS + "y"})
    _rec("TC-R7-12 引号 -t 非 home 目标 → 放行（Q-6-1 负例）", res is None)
    # Q-6-2 重构负例：字面量收敛后行为不回潮
    res = _call("terminal", {"command": "cat " + GUARD + "/handler.py"})
    _rec("TC-R7-13 cat 守卫 handler.py → 放行（Q-6-2 负例）", res is None)
    res = _call("write_file", {"path": PGUARD + BS + "plugin.yaml", "content": "x"})
    _rec("TC-R7-14 write_file 镜像 plugin.yaml → block（Q-6-2 负例保持）", _is_block(res))


def run_r8_fixes():
    """round8 最小化修复回归（F-7-1 续行归一语义重写 + F-7-2 灰区 + 接受边界锁）。"""
    NL, CR, BS, SQ, DQ = chr(10), chr(13), chr(92), chr(39), chr(34)
    GUARD = "D:/myagent/.hermes/plugins/write-guard"
    TD = "--target-directory"
    WS = "D:/myagent/workspace/out"
    # F-7-1（必修）：真续行两形必须封堵——删除式粘连后行直接相接（approve）
    res = _call("terminal", {"command": "cp evil " + BS + NL + GUARD})
    _rec("TC-R8-01 真续行 bs+LF 粘连 cp 守卫目录 → approve（F-7-1）", _is_approve(res))
    res = _call("terminal", {"command": "cp evil " + BS + CR + NL + GUARD})
    _rec("TC-R8-02 真续行 bs+CRLF 粘连 cp 守卫目录 → approve（F-7-1）", _is_approve(res))
    # 成对反斜杠+真换行：粘连不吞转义对，换行仍是分隔符（盲 replace 旧形=旁路，修后拦）
    res = _call("terminal", {"command": "echo a" + BS + BS + NL + "cp evil " + GUARD})
    _rec("TC-R8-03 2bs+LF 分段后 cp 守卫目录 → approve（奇偶成对消耗）", _is_approve(res))
    # 双引号内 bs+LF：引号内不处理（2026-09-22 范围决策排除第 2 条）——锁现状 PASS
    res = _call("terminal", {"command": "echo " + DQ + "a" + BS + NL + GUARD + DQ})
    _rec("TC-R8-04 双引号内 bs+LF 登记形 → 锁现状放行（排除范围2）", res is None)
    res = _call("terminal", {"command": "echo " + SQ + "a" + BS + NL + "cp evil " + GUARD + SQ})
    _rec("TC-R8-05 单引号内 bs+LF 字面不误伤 → 放行", res is None)
    # 奇偶族余项锁现状（登记见 CHANGELOG 接受边界）：3bs=粘连方向 approve；4bs=分段 PASS
    res = _call("terminal", {"command": "cp evil " + BS * 3 + NL + GUARD})
    _rec("TC-R8-06 3bs+LF → approve（粘连已发生未裂段，登记族锁向）", _is_approve(res))
    res = _call("terminal", {"command": "cp evil " + BS * 4 + NL + GUARD})
    _rec("TC-R8-07 4bs+LF → 放行（POSIX 转义对+独立换行，登记族锁向）", res is None)
    # 引号穿插劈 token 形（排除范围第 1 条）：锁现状 PASS，防日后误扩
    res = _call("terminal", {"command": "cp -" + SQ + "t" + SQ + GUARD + " evil"})
    _rec("TC-R8-08 穿插 cp -t 劈token粘连 → 锁现状放行（排除范围1）", res is None)
    # F-7-2（处置=修）：引号长选项词后 = 粘连两形 approve；workspace 负例放行
    res = _call("terminal", {"command": "cp " + SQ + TD + SQ + "=" + GUARD + " x"})
    _rec("TC-R8-09 单引号长选项=粘连 GUARD → approve（F-7-2）", _is_approve(res))
    res = _call("terminal", {"command": "cp " + DQ + TD + DQ + "=" + GUARD + " x"})
    _rec("TC-R8-10 双引号长选项=粘连 GUARD → approve（F-7-2）", _is_approve(res))
    res = _call("terminal", {"command": "cp " + SQ + TD + SQ + "=" + WS + " x"})
    _rec("TC-R8-11 F-7-2 非 home 目标 → 放行（负例）", res is None)
    # 整词包裹在纳入范围（OOB 2026-09-22 口径）：引号包路径必须仍 approve
    res = _call("terminal", {"command": "cp evil " + SQ + GUARD + SQ})
    _rec("TC-R8-12 整词单引号包守卫路径 → approve（纳入范围3锁）", _is_approve(res))
    res = _call("terminal", {"command": "cp evil " + DQ + GUARD + DQ})
    _rec("TC-R8-13 整词双引号包守卫路径 → approve（纳入范围3锁）", _is_approve(res))
    # 红线：gateway 禁令续行两形 block 保持
    res = _call("terminal", {"command": "hermes gateway " + BS + NL + "restart"})
    _rec("TC-R8-14 gateway bs+LF restart → block（红线保持）", _is_block(res))
    res = _call("terminal", {"command": "hermes gateway " + BS + CR + NL + "restart"})
    _rec("TC-R8-15 gateway bs+CRLF restart → block（同源封堵）", _is_block(res))
    # 回归负例零回潮：读 cat / workspace 写
    res = _call("terminal", {"command": "cat " + GUARD + "/handler.py"})
    _rec("TC-R8-16 cat 守卫文件 → 放行（负例回潮哨）", res is None)
    res = _call("terminal", {"command": "echo x > D:/myagent/workspace/a.txt"})
    _rec("TC-R8-17 workspace 写 → 放行（负例回潮哨）", res is None)


def run_scheduler():
    cmd = "echo hi > D:/myagent/.hermes/config.yaml && echo x > " + _TMP_REF
    res = _call("terminal", {"command": cmd})
    ok = isinstance(res, dict) and res.get("action") == "block"
    calls = {"a": 0}
    def _stub_a(tool_name, args, task_id=""):
        calls["a"] += 1
        return {"action": "approve", "message": "stub-a", "rule_key": "x"}
    with _stub_guard("_guard_hermes_config", _stub_a):
        res2 = _call("terminal", {"command": cmd})
        ok = ok and isinstance(res2, dict) and res2.get("action") == "block" and calls["a"] == 0
    _rec("TC-S-01 同时命中 C+A → 只返回 C block（A 未被调用）", ok)
    calls = {"b": 0}
    def _stub_b(tool_name, args, task_id=""):
        calls["b"] += 1
        return {"action": "approve", "message": "stub-b", "rule_key": "x"}
    with _stub_guard("_guard_memory_write", _stub_b):
        res = _call("write_file", {"path": _CFG})
        ok = _is_block(res) and calls["b"] == 0
    _rec("TC-S-02 A 命中即返 block（B 桩未调用）", ok)
    res = _call("write_file", {"path": r"D:\myagent\workspace\a.md"})
    ok = res is None
    res = _call("patch", {"path": r"D:\myagent\workspace\b.py"})
    ok = ok and res is None
    res = _call("terminal", {"command": "echo hello"})
    ok = ok and res is None
    res = _call("execute_code", {"code": "print(1+1)"})
    ok = ok and res is None
    res = _call("read_file", {"path": r"D:\myagent\workspace\x.md"})
    ok = ok and res is None
    res = _call("unknown_tool", {"url": "https://example.com"})
    ok = ok and res is None
    res = _call("hindsight_recall", {"query": "x"})
    ok = ok and res is None
    _rec("TC-S-03 无命中放行（各工具代表）", ok)


# ---------- 守卫异常注入（AC-10 / FR-14） ----------
def run_exception_isolation():
    def _boom(tool_name, args, task_id=""):
        raise RuntimeError("boom")
    with _stub_guard("_guard_hermes_config", _boom), _stub_guard("_guard_memory_write", _boom):
        # C 命中（临时目录）→ 即便 A/B 全炸也必须返回 block（fail-closed 不回退）
        res = _call("terminal", {"command": "echo x > " + _TMP_REF})
        ok = isinstance(res, dict) and res.get("action") == "block"
    _rec("TC-E-01 C 命中不受 A/B 异常影响", ok)

    log_records = []
    class _Capture(_logging.Handler):
        def emit(self, record):
            log_records.append(record.getMessage())
    _cap = _Capture()
    _logger = _logging.getLogger("write_guard_handler")
    _logger.addHandler(_cap)
    _logger.setLevel(_logging.DEBUG)
    try:
        with _stub_guard("_guard_hermes_config", _boom):
            log_records.clear()
            res = _call("write_file", {"path": _CFG})   # 仅 A 面命中，A 炸
            ok = res is None and any("抛出异常" in r for r in log_records)
        _rec("TC-E-02 仅 A 命中且 A 抛异常 → 按未命中放行且日志有记录", ok)

        with _stub_guard("_guard_hermes_config", _boom):
            def _stub_b2(tool_name, args, task_id=""):
                return {"action": "approve", "message": "stub-b", "rule_key": "stub"}
            with _stub_guard("_guard_memory_write", _stub_b2):
                log_records.clear()
                # write_file+_CFG：D 不命中 → C 不命中（路径无 temp 字样）→
                # A 真实命中但抛异常被隔离 → 轮询继续 → B(桩) 命中 approve。
                # 用 write_file 而非 retain：retain 不经过 A，测不到
                # 「A 异常后续轮询」这条语义（独立质量审查后自纠）。
                res = _call("write_file", {"path": _CFG})
                ok = _is_approve(res) and res.get("message") == "stub-b"
            _rec("TC-E-03 A 异常隔离后轮询继续 → 后续守卫命中 approve", ok)

        with _stub_guard("_guard_memory_write", _boom):
            log_records.clear()
            res = _call("hindsight_retain", {"content": "x"})
            ok = res is None and any("抛出异常" in r for r in log_records)
        _rec("TC-E-04 仅 B 命中且 B 抛异常 → 放行且日志有记录", ok)

        with _stub_guard("_guard_hermes_config", _boom), _stub_guard("_guard_memory_write", _boom):
            # A/B 全炸：write_file 目标为配置 → A 面失效按未命中放行（FR-14 语义），
            # 但 C 面终端命中形态仍必须 block —— 插件整体不失效。
            log_records.clear()
            res = _call("write_file", {"path": _CFG})
            ok = res is None
            res2 = _call("terminal", {"command": "echo x > " + _TMP_REF})
            ok = ok and isinstance(res2, dict) and res2.get("action") == "block"
            # D 面同样不受 A/B 异常影响
            res3 = _call("terminal", {"command": "hermes gateway restart"})
            ok = ok and _is_block(res3)
        _rec("TC-E-05 A/B 均异常 → 插件不整体失效，C/D 仍工作", ok)
    finally:
        _logger.removeHandler(_cap)


# ---------- 消息内容断言（AC-01 / FR-06 / FR-09） ----------
def run_messages():
    res = _call("write_file", {"path": _CFG})
    msg = res.get("message", "") if isinstance(res, dict) else ""
    _rec("TC-M-01 message 含原始路径", _CFG in msg)
    _rec("TC-M-02 message 含工具名与 skill 指引",
         "write_file" in msg and "skill" in msg and "safe-config-modify" in msg)
    _rec("TC-M-03 message 含原因字样", "配置写保护" in msg)
    # block 结果无 rule_key（不进审批门）
    _rec("TC-M-04 block 结果无 rule_key", "rule_key" not in res)
    res = _call("hindsight_retain", {"content": "x"})
    msg = res.get("message", "") if isinstance(res, dict) else ""
    _rec("TC-M-05 B message 含工具名与原因", "hindsight_retain" in msg and "记忆写保护" in msg)
    rk = res.get("rule_key", "") if isinstance(res, dict) else ""
    _rec("TC-M-06 B rule_key 精确值", rk == "write_guard:memory:hindsight_retain")
    res_a = _call("write_file", {"path": _CFG})
    res_b = _call("hindsight_retain", {"content": "x"})
    ok = True
    for r in (res_a, res_b):
        if isinstance(r, dict):
            m = r.get("message", "")
            ok = ok and handler._scan("shell", m) is None and handler._scan("code", m) is None
    _rec("TC-M-07 A/B 消息无临时目录字面量", ok)
    saved_cwd = _os.getcwd
    try:
        _os.getcwd = lambda: r"D:\myagent\.hermes"
        res = _call("write_file", {"path": "config.yaml"})
        m1 = res.get("message", "") if isinstance(res, dict) else ""
        ok = _is_block(res) and "config.yaml（对应文件：d:/myagent/.hermes/config.yaml）" in m1
    finally:
        _os.getcwd = saved_cwd
    res = _call("write_file", {"path": r"%HERMES_HOME%\config.yaml"}, hermes_home=_DEFAULT)
    m2 = res.get("message", "") if isinstance(res, dict) else ""
    ok = ok and _is_block(res) and "d:/myagent/.hermes/config.yaml" in m2
    _rec("TC-M-08 变体命中双段展示解析后绝对路径（block）", ok)


# ---------- A 项：review-001 FIX 增补用例（MED-1/MED-2/LOW-1/LOW-2） ----------
def run_a_reviewfix():
    # LOW-1：管道形态——cd 不贪婪吞段，管道两侧独立判定（设计 3.2.2）
    saved_cwd = _os.getcwd
    try:
        _os.getcwd = lambda: r"D:\myagent\workspace"
        res = _call("terminal", {"command": "cd D:/myagent/.hermes | echo hi > config.yaml"})
        ok = res is None                     # 管道左侧 cd 在子进程、不跨管道传播 → 写侧基于原 cwd 未命中
        res = _call("terminal", {"command": "cd D:/other/dir | echo hi > D:/myagent/.hermes/config.yaml"})
        ok = ok and _is_block(res)         # 管道右侧独立判定，绝对路径写形态仍被识别（B3）
    finally:
        _os.getcwd = saved_cwd
    _rec("TC-A-48 管道形态：cd 不吞段、两侧独立判定（LOW-1）", ok)
    # LOW-2：动态 cd 目标（残留环境变量引用）→ 立即放行，不污染后续判定
    res = _call("terminal", {"command": "cd $WGUARD_UNSET_DEST && echo hi > config.yaml"})
    ok = res is None
    res = _call("terminal", {"command": "cd ${WGUARD_UNSET_DEST} && echo hi > D:/myagent/.hermes/config.yaml"})
    ok = ok and res is None                  # 立即 return None：后续受保护写形态也不判定（Q-03）
    _rec("TC-A-49 动态 cd 目标（未解析引用）→ 立即放行（LOW-2）", ok)
    # MED-1：os.open 底层写标志识别（DR-10 / 3.2.3）
    res = _call("execute_code", {"code": "os.open('D:/myagent/.hermes/config.yaml', os.O_WRONLY)"})
    _rec("TC-A-50 os.open 写标志 → block（MED-1 / B3）", _is_block(res))
    res = _call("execute_code", {"code": "os.open('D:/myagent/.hermes/config.yaml', os.O_RDONLY)"})
    _rec("TC-A-51 os.open 只读标志 → 放行（MED-1 负例）", res is None)
    # MED-2：命令输出参数形态（curl -o/-O、wget -O、sort -o 等）
    res = _call("terminal", {"command": "curl -o D:/myagent/.hermes/config.yaml https://x.com"})
    _rec("TC-A-52 curl -o 输出参数为受保护路径 → block（MED-2 / B3）", _is_block(res))
    res = _call("terminal", {"command": "curl -o D:/myagent/workspace/out.html https://x.com"})
    _rec("TC-A-53 curl -o 输出参数为非受保护路径 → 放行（MED-2 负例）", res is None)
    res = _call("terminal", {"command": "wget -O D:/myagent/.hermes/config.yaml https://x.com"})
    ok = _is_block(res)
    res = _call("terminal", {"command": "sort -o D:/myagent/.hermes/config.yaml data.txt"})
    ok = ok and _is_block(res)
    res = _call("terminal", {"command": "curl --output=D:/myagent/.hermes/config.yaml https://x.com"})
    ok = ok and _is_block(res)
    _rec("TC-A-54 wget -O / sort -o / curl --output= → block（MED-2 / B3）", ok)
    res = _call("terminal", {"command": "custom_tool -o D:/myagent/.hermes/config.yaml"})
    _rec("TC-A-55 未知命令含 -o → 无法判定放行（MED-2 低误拦）", res is None)


run_a_basic()
run_a_variants()
run_a_terminal()
run_a_execute_code()
run_a_bounds()
run_a_designfix()
run_a_reviewfix()
run_b()
run_c_readtools()
run_gateway_cmd()
run_sec_bypass()
run_m_fixes()
run_r3_fixes()
run_r5_fixes()
run_r6_fixes()
run_r7_fixes()
run_r8_fixes()
run_x_invariants()
run_scheduler()
run_exception_isolation()
run_messages()
failures.extend(new_failures)
print()
if failures:
    print(f"FAILED: {len(failures)} case(s)")
    for f in failures:
        print("  ", f)
    sys.exit(1)
print(f"ALL PASS ({len(CASES)} scan cases + {HOOK_N} hook cases + {_new_case_count} new cases)")
