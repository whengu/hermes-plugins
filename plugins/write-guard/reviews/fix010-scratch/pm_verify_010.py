import importlib.util, os
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
spec = importlib.util.spec_from_file_location("wg", r"D:\myagent\workspace\write-guard\handler.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
CFG = "D:" + B + "myagent" + B + ".hermes" + B + "config.yaml"
CFGS = CFG.replace(B, "/")
HD = "D:" + B + "myagent" + B + ".hermes" + B + "plugins" + B + "write-guard" + B + "handler.py"
def j(cmd):
    r = m._judge_terminal(cmd, "terminal")
    return "block/approve" if r else "PASS"
print("== F-9-1 复制不拦红线（Copy-Item/Tee-Object 源位/目标位）==")
print("1a Copy-Item CFG 备份位(ws) 应放行:", j("Copy-Item " + CFG + " D:" + B + "myagent" + B + "workspace" + B + "bak.yaml"))
print("1b pwsh Copy-Item CFG 备份位     :", j('pwsh -Command "Copy-Item ' + CFGS + ' D:/myagent/workspace/bak.yaml"'))
print("1c cp CFG 备份位(对照既有)        :", j("cp " + CFG + " D:" + B + "myagent" + B + "workspace" + B + "bak.yaml"))
print("1d Copy-Item evil CFG 目标位应拦  :", j("Copy-Item evil " + CFG))
print("1e Tee-Object 源位读非守卫        :", j("Tee-Object -FilePath D:" + B + "myagent" + B + "workspace" + B + "out.txt"))
print("== F-9-2 wrapper x 载体组合 ==")
print("2a sudo bash -c \"cp evil HD\"     :", j('sudo bash -c "cp evil ' + HD + '"'))
print("2b bash -c \"cp evil HD\" 对照     :", j('bash -c "cp evil ' + HD + '"'))
print("2c sudo cmd /c copy evil CFG      :", j('sudo cmd /c copy evil ' + CFGS))
print("== F-9-3 cmd sort /O 方言 ==")
print("3a sort /O CFG d.txt              :", j("sort /O " + CFGS + " d.txt"))
print("3b sort /O" + CFGS + " d.txt 粘连   :", j("sort /O" + CFGS + " d.txt"))
print("3c bash -c \"sort /O CFG d.txt\"    :", j('bash -c "sort /O ' + CFGS + ' d.txt"'))
print("== F-9-4 tee 非末位目标 ==")
print("4a tee evil CFG                   :", j("tee evil " + CFG))
print("4b tee CFG evil 对照末位目标      :", j("tee " + CFG + " evil"))
print("== 红线回归 ==")
print("R1 gateway block                  :", j("hermes gateway " + chr(92) + "\nrestart") != "PASS")
print("R2 cp 配置写弹卡                  :", j("cp evil " + CFG))
