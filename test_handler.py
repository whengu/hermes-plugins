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
for name, ok in [("hook-block-terminal", ok1), ("hook-pass-terminal", ok2),
                 ("hook-fallback-unknown-block", ok3), ("hook-fallback-unknown-pass", ok4)]:
    print(f"[{'OK ' if ok else 'FAIL'}] hook: {name}")
    if not ok:
        failures.append(("hook", name, None, None))

print()
if failures:
    print(f"FAILED: {len(failures)} case(s)")
    for f in failures:
        print("  ", f)
    sys.exit(1)
print(f"ALL PASS ({len(CASES)} scan cases + 4 hook cases)")
