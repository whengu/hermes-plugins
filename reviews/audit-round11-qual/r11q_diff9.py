
import importlib.util
def load(p,n):
    spec = importlib.util.spec_from_file_location(n,p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
r9 = load("reviews/audit-round10-sec/handler_r9_cbd6301.py","r9")
new = load("handler.py","new")
HOME = new._hermes_home(); CFG = HOME+"/config.yaml"; WS="D:/myagent/workspace/a.txt"; GD=HOME+"/plugins/write-guard/handler.py"
def act(h,cmd):
    r = h.on_pre_tool_call("terminal", {"command": cmd})
    return "PASS" if r is None else r.get("action","?")
cmds = [
 f"cp {WS} {CFG}", f"cp {CFG} {WS}", f"cp {WS} -t {HOME}", f"rsync -t {CFG} {WS}",
 f"rsync -av {CFG} {WS}", f"install {WS} {CFG}", f"cp evil.py {GD}",
 f"cp {WS} {GD}", f"Copy-Item -Container {CFG} -Destination {WS}",
 f"Copy-Item {CFG} D:/myagent/bak.yaml", f"tee {CFG} out2",
 f"echo x|tee {CFG}", f"cmd /c copy /Y {WS} {CFG}",
]
for c in cmds:
    o,n = act(r9,c), act(new,c)
    print(("SAME" if o==n else "DIFF"), f"r9={o:8s} r11={n:8s}  {c[:66]}")
