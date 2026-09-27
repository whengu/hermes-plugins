# round10 安全路探针 E：F-9-3 邻域深挖（-O URL 粘连面、/O= 形）+ F-9-2 全路径载体归因 + tee 非可运行形核实
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

def cmp(group, cases):
    print("---", group, "---")
    for tag, cmd in cases:
        print(f"  new={act(h,cmd):7s} old={act(ho,cmd):7s}  {tag} :: {cmd!r}")

# F-9-3 修复的 URL 邻域：-O/-o 粘连值非保护、粘连 URL、/O= 形
cmp("URL 邻域 / 粘连等号形", [
    ("curl -O粘连URL(登记先例 非可运行)", "curl -Ohttp://x/a.txt"),
    ("curl -O=URL", "curl -O=http://x/a.txt"),
    ("wget -O=URL", "wget -O=http://x/a.txt"),
    ("wget -O 粘连非保护", "wget -O" + WS + " http://x"),
    ("sort /O=CFG 等号粘连", "sort /O=" + CFG + " d.txt"),
    ("sort /O=ws", "sort /O=" + WS + " d.txt"),
    ("sort -O=CFG", "sort -O=" + CFG + " d.txt"),
    ("sort --output=CFG 对照", "sort --output=" + CFG + " d.txt"),
    ("sort /O 粘连CFG", "sort /O" + CFG + " d.txt"),
    ("curl -O /CFG 空格+绝对路径", "curl -O " + CFG + " http://x"),
    ("wget /O CFG", "wget /O " + CFG + " http://x"),
    ("sort /o 小写粘连", "sort /o" + CFG + " d.txt"),
    ("curl 前置-o粘连cluster 对照", "curl -sSLO " + CFG),
])
# F-9-4 邻域：非可运行形核实 + 可运行变体
cmp("tee 粘连/cluster 形", [
    ("tee -a<CFG> 非可运行形?", "tee -a" + CFG),
    ("tee -ia<CFG> 非可运行形?", "tee -ia" + CFG),
    ("tee -a <CFG> 空格(应block)", "tee -a " + CFG),
    ("tee --append <CFG>(应block)", "tee --append " + CFG),
    ("tee -a cluster 多目标", "tee -a e " + CFG),
    ("TEEOBJ 词内不误", "teeobjtool x " + CFG),
    ("路径含 tee 不误", "D:/myagent/workspace/tee/run.sh " + CFG),
])
# F-9-2 归因：全路径载体是否受剥离链影响（附录③ vs 新面）
cmp("全路径/引号载体归因", [
    ("/usr/bin/bash -c 载体(附录③候选)", "/usr/bin/bash -c " + q2 + "cp evil " + GUARD + q2),
    ("D:/tools/bash -c 载体", "D:/tools/bash -c " + q2 + "cp evil " + GUARD + q2),
    ("'bash' -c 引号包载体", q2 + "bash" + q2 + " -c " + q2 + "cp evil " + GUARD + q2),
    ("./bash -c 相对载体", "./bash -c " + q2 + "cp evil " + GUARD + q2),
    ("bash 全路径+wrapper", "sudo /usr/bin/bash -c " + q2 + "echo x > " + CFG + q2),
])
# 名实观测
print("--- 观测 ---")
import inspect
print("_OUTPUT_FLAG_EQ_RE 模式:", h._OUTPUT_FLAG_EQ_RE.pattern)
print("_GLUED_O_RE 模式:", h._GLUED_O_RE.pattern)
print("_prev_command_word 仍在模块:", hasattr(h, "_prev_command_word"))
print("cw('findstr /O x f') =", h._command_word("findstr /O x f"))
print("cw('sort /O=x d') =", h._command_word("sort /O=" + CFG + " d.txt"))
print("glued match '/O='+CFG:", bool(h._GLUED_O_RE.match("/O=" + CFG)))
