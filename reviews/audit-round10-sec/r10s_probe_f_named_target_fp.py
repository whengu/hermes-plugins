# round10 安全路探针 F：命名目标位参邻域（-Destination 前置位）+ F-9-3 FP 族归因（新旧对照）
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
GUARD = HOME + "/plugins/write-guard"

def act(mod, cmd):
    r = mod.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action", "PASS")

def cmp(group, cases, want=None):
    print("---", group, "---")
    for tag, cmd in cases:
        n, o = act(h, cmd), act(ho, cmd)
        flag = "" if want is None else ("  <== 预期 " + want if (n != want) else "")
        print(f"  new={n:7s} old={o:7s}  {tag} :: {cmd!r}{flag}")

# 命名目标前置位（-t 同语义面）
cmp("PS 命名目标前置位", [
    ("Copy-Item -Destination CFG evil(目标前置)", "Copy-Item -Destination " + CFG + " " + WS),
    ("对照 cp -t CFG evil", "cp -t " + CFG + " " + WS),
    ("对照 cp --target-directory=CFG evil", "cp --target-directory=" + CFG + " " + WS),
    ("Tee-Object -FilePath CFG -InputObject x", "Tee-Object -FilePath " + CFG + " -InputObject x"),
    ("Copy-Item -LiteralPath evil -Destination CFG(尾位)", "Copy-Item -LiteralPath " + WS + " -Destination " + CFG),
    ("载体内 -Destination 前置", "pwsh -Command " + q2 + "Copy-Item -Destination " + CFG + " " + WS + q2),
])
# F-9-3 FP 族归因：dash 形是否两代同陷（先例定位）
cmp("FP 族 dash 对照（旧代是否同陷）", [
    ("sort dir-o CFG（dash 结尾旧面）", "sort D:/myagent/workspace/my-dir-o " + CFG),
    ("sort dir/o CFG（slash 新引入）", "sort D:/myagent/workspace/o " + CFG),
    ("sort dir/O CFG 大写", "sort D:/myagent/workspace/O " + CFG),
    ("curl url/o CFG", "curl http://x/o " + CFG),
    ("wget f/o CFG", "wget http://x/f/o " + CFG),
    ("sort 引号 '/o' CFG", "sort " + q2 + "D:/myagent/workspace/o" + q2 + " " + CFG),
    ("门内但目标非保护 sort /o x", "sort D:/myagent/workspace/o " + WS),
])
# 死函数观测 + 行为记录（附录素材）
print("--- 观测 ---")
import re as _re
src = open(os.path.join(HERE, "..", "..", "handler.py"), encoding="utf-8").read()
print("_prev_command_word 引用数(含定义):", len(_re.findall(r"_prev_command_word", src)))
print("cw('sort D:/x/o CFG') =", h._command_word("sort D:/x/o " + CFG))
print("Tee-Object CFG 新代际:", act(h, "Tee-Object " + CFG))
print("tee CFG 新代际:", act(h, "tee " + CFG))
