# round10 安全路探针 G：F-9-1 新 FP 候选定位（命名目标前置位）+ 反向语义确认 + 锁定向核对
import importlib.util, os
BS, q2 = chr(92), chr(34)
os.environ["HERMES_HOME"] = "D:" + BS + "myagent" + BS + ".hermes"
os.chdir("D:" + BS + "myagent" + BS + "workspace")
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("hg", os.path.join(HERE, "..", "..", "handler.py"))
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
ospec = importlib.util.spec_from_file_location("ho", os.path.join(HERE, "handler_r9_cbd6301.py"))
ho = importlib.util.module_from_spec(ospec); ospec.loader.exec_module(ho)
HOME = "D:/myagent/.hermes"
CFG = HOME + "/config.yaml"
WS = "D:/myagent/workspace/a.txt"
BAK = "D:/myagent/workspace/bak.yaml"
GUARD = HOME + "/plugins/write-guard"

def act(mod, cmd):
    r = mod.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action", "PASS")

cases = [
 ("F10候选-1 命名目标前置位(CFG=写目标)", "Copy-Item -Destination " + CFG + " " + WS),
 ("F10候选-2 Tee -FilePath 前置+后续位参", "Tee-Object -FilePath " + CFG + " -InputObject x"),
 ("候选-3 反向：目标已绑非保护+尾位受保护源", "Copy-Item -Destination " + BAK + " " + CFG),
 ("候选-4 反向多源尾位 CFG", "Copy-Item -Destination " + BAK + " " + WS + " " + CFG),
 ("对照-5 尾位命名目标(修前修后都应approve)", "Copy-Item " + WS + " -Destination " + CFG),
 ("对照-6 cp -t 前置形", "cp -t " + CFG + " " + WS),
 ("对照-7 载体内前置形", 'pwsh -Command "Copy-Item -Destination ' + CFG + " " + WS + '"'),
 ("对照-8 Copy-Item 位置形 CFG 目标?（源位在首）", "Copy-Item " + BAK + " " + CFG),
]
print("--- new vs old(round9 cbd6301) ---")
for tag, c in cases:
    n, o = act(h, c), act(ho, c)
    print(f"  new={n:7s} old={o:7s}  {tag} :: {c!r}")
# token 级归因：前置位形里 CFG 是否“末位路径参数”
seg = "Copy-Item -Destination " + CFG + " " + WS
ptoks = list(h._PATH_TOKEN_RE.finditer(seg))
print("路径 token 序:", [t.group(0)[-22:] for t in ptoks])
print("CFG 是末位 token:", ptoks and ptoks[-1].group(0) == CFG)
print("cw =", h._command_word(seg))
