
import importlib.util
def load(p,n):
    spec = importlib.util.spec_from_file_location(n,p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
old = load("reviews/audit-round10-qual/base/handler_r10commit.py","r10")
new = load("handler.py","r11")
HOME = new._hermes_home(); CFG = HOME+"/config.yaml"; WS="D:/myagent/workspace/a.txt"
def act(h,cmd):
    r = h.on_pre_tool_call("terminal", {"command": cmd})
    return "PASS" if r is None else r.get("action","?")
susp = [
 f"Copy-Item -Path {CFG} {WS}",              # PS: Path=源，末位=目标WS 非保护 → 语义读，应PASS?
 f"Copy-Item -LiteralPath {CFG} D:/x/b.txt", # 同上源位绑定
 f"Copy-Item -Path {CFG} -Destination {WS}", # 双命名 目标非保护 → PASS(已证)
 f"Copy-Item {WS} -Destination {CFG}",       # 正常目标绑定末位
 f"Copy-Item -Destination {WS} -Path {CFG}", # 先dest后path 源绑定
 f"Tee-Object -FilePath {CFG}",              # tee目标 前置唯一
 f"Copy-Item -Container {CFG} {WS}",         # Container非Copy-Item实参(冷形)
 f"cp -Path {CFG} {WS}",                     # 非PS命令零差
 f"Install-Module x; Copy-Item -Path {CFG} {WS}",
]
for c in susp:
    o,n = act(old,c), act(new,c)
    print(("SAME" if o==n else "DIFF"), f"r10={o:8s} r11={n:8s}  {c[:60]}")
