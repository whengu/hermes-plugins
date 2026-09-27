import importlib.util, os, sys
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
W = r"D:\myagent\workspace\write-guard"
CFGS = "D:/myagent/.hermes/config.yaml"
WSX = "D:/myagent/workspace/x.txt"
GENS = [
    ("r9 cbd6301", W + B + "reviews" + B + "audit-round10-sec" + B + "handler_r9_cbd6301.py"),
    ("r11 94998f5", W + B + "_r2tmp" + B + "handler_r11_94998f5.py"),
    ("r12 4e254c8", W + B + "_r2tmp" + B + "r13q" + B + "h_4e254c8.py"),
    ("r13 HEAD", W + B + "handler.py"),
]
CASES = [
    ("A: Copy -Path ws <CFG-pos>",  f"Copy-Item -Path {WSX} {CFGS}"),
    ("B: Copy <src> <CFG-pos>",     f"Copy-Item {WSX} {CFGS}"),
    ("C: Copy -Path ws CFG -Recurse", f"Copy-Item -Path {WSX} {CFGS} -Recurse"),
    ("D: Copy -Destination ws CFG(K11)", f"Copy-Item -Destination {WSX} {CFGS}"),
    ("E: Tee -InputObject x <CFG-pos>", f"Tee-Object -InputObject x {CFGS}"),
]
mods = []
for name, p in GENS:
    spec = importlib.util.spec_from_file_location("g" + name[:2], p)
    mm = importlib.util.module_from_spec(spec); spec.loader.exec_module(mm)
    mods.append((name, mm))
for cname, cmd in CASES:
    row = []
    for name, mm in mods:
        r = mm._judge_terminal(cmd, "terminal")
        row.append(f"{name}={'PASS' if r is None else r.get('action')}")
    print(f"{cname:40s} " + " | ".join(row))
# on_pre_tool_call red lines, independent
import json
def hook(cmd):
    r = None
    out = sys.stdout
    return m2hook(cmd)
m2 = mods[-1][1]
def act(cmd):
    res = m2.on_pre_tool_call("terminal", {"command": cmd, "workdir": os.getcwd()}, task_id="q13")
    if res is None: return "PASS"
    if isinstance(res, dict): return str(res.get("action"))
    return str(res)
print("红线1 gateway restart:", act("hermes gateway restart"))
print("红线2 cp 写配置:", act("cp evil " + CFGS))
print("红线3 Copy-Item 源位读:", act("Copy-Item " + CFGS + " " + WSX))
print("红线4 rm -r (approvals 层外, 四守卫应 PASS):", act("rm -rf D:/myagent/workspace/z") )
