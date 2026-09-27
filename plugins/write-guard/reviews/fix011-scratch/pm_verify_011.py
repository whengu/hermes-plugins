import importlib.util, os, subprocess
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
W = r"D:\myagent\workspace\write-guard"
spec = importlib.util.spec_from_file_location("wg", W + B + "handler.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
CFG = "D:" + B + "myagent" + B + ".hermes" + B + "config.yaml"
CFGS = CFG.replace(B, "/")
WSO = "D:/myagent/workspace/o"
def j(cmd):
    r = m._judge_terminal(cmd, "terminal")
    return "PASS" if r is None else str(r.get("action"))
print("== F-10-1 五向 + 组合面 ==")
print("i Copy-Item -Destination CFG 非保护   :", j("Copy-Item -Destination " + CFGS + " D:/myagent/workspace/x.txt"))
print("j Tee-Object -FilePath CFG -InputObj  :", j("Tee-Object -FilePath " + CFGS + " -InputObject x"))
print("k pwsh载体 \"Copy-Item -Destination…\"   :", j('pwsh -Command "Copy-Item -Destination ' + CFGS + ' D:/myagent/workspace/x.txt"'))
print("l sudo pwsh -Command 同形              :", j('sudo pwsh -Command "Copy-Item -Destination ' + CFGS + ' D:/myagent/workspace/x.txt"'))
print("m 反向 -Destination 非保护 CFG(源)应PASS:", j("Copy-Item -Destination D:/myagent/workspace/x.txt " + CFGS))
print("n 尾位 -Destination CFG (r10 锁形应保持):", j("Copy-Item evil.txt -Destination " + CFGS))
print("== F-10-2 四形 + 对照锁形 ==")
print("o sort ws/o CFG                        :", j("sort " + WSO + " " + CFGS))
print("p sort ws/O CFG                        :", j("sort " + "D:/myagent/workspace/O" + " " + CFGS))
print("q curl http://x/o CFG                  :", j("curl http://x/o " + CFGS))
print("r wget http://x/f/o CFG                :", j("wget http://x/f/o " + CFGS))
print("s 附录⑥ sort ws/my-dir-o CFG 两代同陷   :", j("sort D:/myagent/workspace/my-dir-o " + CFGS))
print("t 对照 curl -O URL (必须仍PASS)         :", j("curl -O http://x/a.zip"))
print("u 对照 curl -o CFG (必须仍approve/block):", j("curl -o " + CFGS + " http://x"))
print("v 对照 sort /O CFG (F-9-3 锁, 必须block):", j("sort /O " + CFGS + " d.txt"))
print("w 对照 curl -sSL -oCFG (粘连必须命中)    :", j("curl -sSL -o" + CFGS + " http://x"))
