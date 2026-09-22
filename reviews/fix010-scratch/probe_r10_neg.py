# round10 修复中负例/四向锁探针（载荷全文件内构造，命令行零载荷——round7 教训①）
import importlib.util, os
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
spec = importlib.util.spec_from_file_location(
    "wg10p", "D:" + B + "myagent" + B + "workspace" + B + "write-guard" + B + "handler.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
HOME = "D:/myagent/.hermes"
CFG = HOME + "/config.yaml"
GD = HOME + "/plugins/write-guard"
HD = GD + "/handler.py"
BAK = "D:/myagent/workspace/bak.yaml"


def j(c):
    r = m._judge_terminal(c, "terminal")
    return r.get("action") if isinstance(r, dict) else "PASS"


print("--- F-9-1 四向锁 ---")
print("A 源位 PASS              :", j("Copy-Item " + CFG + " " + BAK))
print("F 目标写配置 approve     :", j("Copy-Item " + BAK + " " + CFG))
print("目标写守卫文件(cp同向)   :", j("Copy-Item evil " + HD))
print("目标写守卫目录 approve   :", j("Copy-Item evil " + GD))
print("cp 源位对照              :", j("cp " + CFG + " " + BAK))
print("cp 目标守卫对照          :", j("cp evil " + GD))
print("Tee-Object 目标写配置    :", j("Tee-Object evil " + CFG))
print("Set-Content 出现即写不回潮:", j("Set-Content " + CFG + " x"))
print("Add-Content 不回潮       :", j("Add-Content " + CFG + " x"))
print("Out-File 不回潮          :", j("Out-File " + CFG))
print("--- F-9-2 负例必测 ---")
print("env|grep                :", j("env | grep config"))
print("time ls                 :", j("time ls D:/myagent/workspace"))
print("nohup python x &        :", j("nohup python x &"))
print("sudo cmd /c copy evil CFG:", j("sudo cmd /c copy evil " + CFG))
print('sudo bash -c "echo>CFG" :', j('sudo bash -c "echo x > ' + CFG + '"'))
print("sudo cat 守卫读         :", j("sudo cat " + HD))
print("--- F-9-3 负例必测 ---")
print("findstr /O x f(门外)    :", j("findstr /O x f"))
print("curl -O URL             :", j("curl -O http://x/a.txt"))
print("curl -oL cluster        :", j("curl -oL http://x/a.txt"))
print("sort -o CFG(仍block)    :", j("sort -o " + CFG + " d.txt"))
print("grep -o x f             :", j("grep -o x f"))
print("mount -o rem,rw         :", j("mount -o rem,rw /dev/sda1"))
print("sort /O 至 workspace    :", j("sort /O D:/myagent/workspace/o.txt d.txt"))
print("--- F-9-4 负例 ---")
print("cat x | tee ws 非保护   :", j("cat x | tee D:/myagent/workspace/log.txt"))
print("2>&1|tee TEMP 既有TC向  :", j("node run.js 2>&1 | tee $env:TEMP\\log.txt"))
print("--- Q9-N2 实测：bash --login -c 双横杠打断 ---")
print('bash --login -c "cp evil GD":', j('bash --login -c "cp evil ' + GD + '"'))
print("--- Q9-N1 实测：全路径命令词两代同向 ---")
print("/usr/bin/ls cp 守卫     :", j("/usr/bin/ls cp evil " + GD))
