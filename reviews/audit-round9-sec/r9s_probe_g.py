# round9 安全路探针 G：新旧代际对照（立项候选是否本轮引入 FP/旁路）
# old=git 1889ba6 handler_old.py；new=工作区 handler.py
import importlib.util, os
BS = chr(92)
os.environ["HERMES_HOME"] = "D:" + BS + "myagent" + BS + ".hermes"
os.chdir("D:" + BS + "myagent" + BS + "workspace")
HERE = os.path.dirname(os.path.abspath(__file__))
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
ho = load("ho", os.path.join(HERE, "scratch", "handler_old.py"))
hn = load("hn", os.path.join(HERE, "..", "..", "handler.py"))
CFG = "D:/myagent/.hermes/config.yaml"
GUARD = "D:/myagent/.hermes/plugins/write-guard"
BAK = "D:/myagent/workspace/config.bak.yaml"
q2 = chr(34)
cases = [
    "Copy-Item " + CFG + " " + BAK,                                   # F-9-2 源位 FP
    'pwsh -Command "Copy-Item ' + CFG + ' ' + BAK + '"',              # F-9-2 内嵌源位
    "pwsh -Command Copy-Item " + CFG + " " + BAK,                     # 裸形源位
    "sort /O " + CFG + " d.txt",                                      # F-9-3 cmd 方言
    "sort /O" + CFG + " d.txt",
    "sudo bash -c " + q2 + "cp evil " + GUARD + q2,                   # F-9-4 wrapper×载体
    "sudo cmd /c copy evil " + CFG,
    "sudo sh -c cp evil " + GUARD,
    "time sudo bash -c " + q2 + "cp evil " + GUARD + q2,
    "cp.exe evil " + GUARD,                                           # 既有 .exe 面(非回归对照)
    "cp " + CFG + " " + BAK,                                          # cp 源位基准 PASS
    "curl -o" + CFG + " http://x",                                    # S-1 封堵对照
    "echo x & cp evil " + GUARD,                                      # S-3 封堵对照
    "cmd /c copy evil " + CFG,                                        # S-5 封堵对照
]
def act(h, c):
    r = h.on_pre_tool_call("terminal", {"command": c})
    return (r or {}).get("action", "PASS")
print(f"{'old':8s}{'new':8s}case")
for c in cases:
    print(f"{act(ho,c):8s}{act(hn,c):8s}{c!r}")
