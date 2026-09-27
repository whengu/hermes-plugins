"""真阳性基线：每条规则至少一个必须命中的样本，锚定守卫确实在工作。"""
from _common import run, CFG

print("== baseline: 预期全部非 PASS ==")
run("D0", "terminal", {"command": "hermes gateway restart"}, "BLOCK")
run("A0", "write_file", {"path": CFG}, "BLOCK")
run("A0b", "patch", {"path": CFG, "old_string": "x", "new_string": "y"}, "BLOCK")
run("A0c", "terminal", {"command": f"echo evil > {CFG}"}, "BLOCK")
run("A0d", "execute_code", {"code": f"open(r'{CFG}', 'w').write('x')"}, "BLOCK")
run("A0e", "terminal", {"command": f"cp workspace/x.yaml {CFG}"}, "APPROVE")
run("B0", "memory", {"action": "add", "content": "x"}, "APPROVE")
run("B0b", "hindsight_retain", {"text": "x"}, "APPROVE")
run("C0", "terminal", {"command": "curl -o /tmp/x.html https://x.com"}, "BLOCK")
run("C0b", "execute_code", {"code": "import tempfile; tempfile.mkdtemp()"}, "BLOCK")
run("C0c", "chrome_take_screenshot", {"filePath": r"C:\Users\x\AppData\Local\Temp\a.png"}, "BLOCK")
run("C0d", "terminal", {"command": 'printf x > "$TMP/f"'}, "BLOCK")
run("C0e", "terminal", {"command": "mktemp"}, "BLOCK")
