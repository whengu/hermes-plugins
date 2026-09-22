# round10 安全路探针 C：F-9-3（sort /O 方言 + -O URL 邻域回退）与 F-9-4（tee 段命令词）复测
import importlib.util, os
BS, q2 = chr(92), chr(34)
os.environ["HERMES_HOME"] = "D:" + BS + "myagent" + BS + ".hermes"
os.chdir("D:" + BS + "myagent" + BS + "workspace")
spec = importlib.util.spec_from_file_location("hg", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "handler.py"))
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
HOME = "D:/myagent/.hermes"
CFG = HOME + "/config.yaml"
WS = "D:/myagent/workspace/a.txt"

# 双代际对照（old=round9 cbd6301 快照，判定「新面由谁引入」用）
import subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
OLD = os.path.join(HERE, "..", "audit-round9-sec", "scratch", "handler_old.py")
ospec = importlib.util.spec_from_file_location("ho", OLD)
ho = importlib.util.module_from_spec(ospec); ospec.loader.exec_module(ho)

def act(mod, cmd):
    r = mod.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action", "PASS")

def run(group, cases):
    print("---", group, "---")
    for tag, cmd, want in cases:
        got = act(h, cmd); old = act(ho, cmd)
        print(f"[{'ok  ' if got==want else 'DIFF'}] new={got:7s} want={want:7s} old={old:7s} {tag} :: {cmd!r}")

# F-9-3 攻击面
run("F-9-3 封堵向", [
    ("sort /O CFG", "sort /O " + CFG + " d.txt", "block"),
    ("sort /O 粘连", "sort /O" + CFG + " d.txt", "block"),
    ("SORT /O 大写", "SORT /O " + CFG + " d.txt", "block"),
    ("sort /o 小写方言", "sort /o " + CFG + " d.txt", "block"),
    ("cmd /c sort /O", "cmd /c sort /O " + CFG + " d.txt", "block"),
    ("sudo sort /O", "sudo sort /O " + CFG + " d.txt", "block"),
    ("链式 sort /O", "dir && sort /O " + CFG + " d.txt", "block"),
    ("反斜杠路径 /O", "sort /O D:" + BS + "myagent" + BS + ".hermes" + BS + "config.yaml d.txt", "block"),
    ("sort -o 对照不回潮", "sort -o " + CFG + " d.txt", "block"),
    ("内嵌 bash -c sort /O", "bash -c " + q2 + "sort /O " + CFG + " d.txt" + q2, "block"),
])
# F-9-3 邻域回退：-O URL 族、门外命令、非保护目标
run("F-9-3 邻域负例（回退/误拦检查）", [
    ("curl -O URL 红线", "curl -O http://x/a.txt", "PASS"),
    ("curl -O 大写 URL", "curl -O https://x/o", "PASS"),
    ("curl -oL cluster", "curl -oL http://x/a.txt", "PASS"),
    ("wget -O 非保护对照", "wget -O " + WS + " http://x", "PASS"),
    ("wget -O CFG 对照", "wget -O " + CFG + " http://x", "block"),
    ("grep -o 门外", "grep -o pat " + CFG, "PASS"),
    ("findstr /O 门外", "findstr /O x f", "PASS"),
    ("mount -o rem,rw 门外", "mount -o rem,rw /dev/sda1", "PASS"),
    ("tar -O 门外", "tar -O -cf - " + CFG, "PASS"),
    ("sort /D 非输出选项", "sort /D " + WS + " d.txt", "PASS"),
    ("sort 只读两文件", "sort " + WS + " d.txt", "PASS"),
    ("curl --output=CFG 长形对照", "curl --output=" + CFG + " http://x", "block"),
])
# F-9-3 新增 FP 候选（/o 结尾路径 token × 门内命令 × 受保护路径后随）
run("F-9-3 FP 候选：/-o 结尾前词", [
    ("sort dir/o CFG（读列表，预测应 PASS）", "sort D:/myagent/workspace/o " + CFG, "PASS"),
    ("curl URL/o CFG", "curl http://x/o " + CFG, "PASS"),
    ("old 代际对照 sort dir/o CFG", "sort D:/myagent/workspace/o " + CFG, "PASS"),
])
# F-9-4 攻击面
run("F-9-4 封堵向", [
    ("tee 非末位", "echo x | tee evil.txt " + CFG, "block"),
    ("tee -a 多目标", "tee -a evil.txt " + CFG, "block"),
    ("tee 三目标中位", "tee a " + CFG + " b", "block"),
    ("tee -i 首位", "tee -i " + CFG, "block"),
    ("sudo tee CFG", "sudo tee " + CFG, "block"),
    ("pwsh 别名 tee evil CFG", "pwsh -Command " + q2 + "tee evil " + CFG + q2, "block"),
    ("内嵌 bash -c tee 非末位", "bash -c " + q2 + "echo y | tee e " + CFG + q2, "block"),
    ("tee CFG out2 对照", "tee " + CFG + " out2.txt", "block"),
])
run("F-9-4 负例", [
    ("cat x | tee ws 非保护", "cat x | tee " + WS, "PASS"),
    ("tee 仅非保护", "tee a.txt b.txt", "PASS"),
    ("atelog 词内 tee 不误", "mytool --x " + CFG, "PASS"),
    ("ls tee/ 目录", "ls D:/myagent/workspace/tee " + CFG, "PASS"),
])
