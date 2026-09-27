import importlib.util, os
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
spec = importlib.util.spec_from_file_location("wg", r"D:\myagent\workspace\write-guard\handler.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
CFG = "D:" + B + "myagent" + B + ".hermes" + B + "config.yaml"
CFGS = CFG.replace(B, "/")
BAK = "D:" + B + "myagent" + B + "workspace" + B + "bak.yaml"
BAKS = BAK.replace(B, "/")
GD = "D:" + B + "myagent" + B + ".hermes" + B + "plugins" + B + "write-guard"
def j(cmd):
    r = m._judge_terminal(cmd, "terminal")
    if r is None: return "PASS"
    return str(r.get("action")) if isinstance(r, dict) else "?" + str(r)[:40]
print("== F-9-1 精确形（报告 §27-36）==")
print("A Copy-Item CFG BAK                :", j("Copy-Item " + CFG + " " + BAK))
print("B -Container CFG -Destination BAK  :", j("Copy-Item -Container " + CFG + " -Destination " + BAK))
print("C pwsh 载体 \"Copy-Item CFG BAK\"    :", j('pwsh -Command "Copy-Item ' + CFGS + " " + BAKS + '"'))
print("D Tee-Object 源位读 -FilePath ws   :", j("Tee-Object -FilePath " + BAK))
print("E 对照 cp CFG BAK                  :", j("cp " + CFG + " " + BAK))
print("F Copy-Item BAK CFG(目标位应拦)    :", j("Copy-Item " + BAK + " " + CFG))
print("== F-9-3 精确形 ==")
print("G sort /O CFG d.txt                :", j("sort /O " + CFGS + " d.txt"))
print("H sort /O" + CFGS + " d.txt 粘连    :", j("sort /O" + CFGS + " d.txt"))
print("I SORT /O 大写                     :", j("SORT /O " + CFGS + " d.txt"))
print("J cmd /c sort /O …                 :", j("cmd /c sort /O " + CFGS + " d.txt"))
print("K sort -o CFG (对照S-1)            :", j("sort -o " + CFGS + " d.txt"))
print("== F-9-4 精确形 ==")
print("L echo x | tee evil.txt CFG        :", j("echo x | tee evil.txt " + CFGS))
print("M tee -a evil.txt CFG              :", j("tee -a evil.txt " + CFGS))
print("N tee CFG out2 (对照首目标)        :", j("tee " + CFGS + " out2.txt"))
print("O pwsh 别名 tee evil CFG           :", j('pwsh -Command "tee evil ' + CFGS + '"'))
print("== F-9-2 复核 + 通道巧合验证 ==")
print("P sudo bash -c cp evil GD          :", j('sudo bash -c "cp evil ' + GD + '"'))
print("Q LANG=C pwsh -Command Copy-Item…  :", j("LANG=C pwsh -Command Copy-Item evil " + CFGS))
