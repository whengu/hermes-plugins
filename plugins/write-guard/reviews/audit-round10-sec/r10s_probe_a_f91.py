# round10 安全路探针 A：F-9-1 复测——复制族四向、cp 同语义一致性、Tee-Object 形、FP 面
# 载荷文件内构造。入口=on_pre_tool_call（round10-context §24 口径）。
import importlib.util, os
BS, q2 = chr(92), chr(34)
os.environ["HERMES_HOME"] = "D:" + BS + "myagent" + BS + ".hermes"
os.chdir("D:" + BS + "myagent" + BS + "workspace")
spec = importlib.util.spec_from_file_location("hg", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "handler.py"))
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
HOME = "D:/myagent/.hermes"
CFG = HOME + "/config.yaml"
BAK = "D:/myagent/workspace/bak.yaml"
WS = "D:/myagent/workspace/a.txt"
GUARD = HOME + "/plugins/write-guard"
HD = GUARD + "/handler.py"

def term(cmd):
    r = h.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action", "PASS")

def run(group, cases):
    print("---", group, "---")
    for tag, cmd, want in cases:
        got = term(cmd)
        mark = "ok  " if got == want else "DIFF"
        print(f"[{mark}] {got:7s} want={want:7s} {tag} :: {cmd!r}")

# 四向锁①源位不拦（红线：复制不拦）
run("①源位读 PASS", [
    ("Copy-Item 位置源位", "Copy-Item " + CFG + " " + BAK, "PASS"),
    ("Copy-Item -Path 命名源", "Copy-Item -Path " + CFG + " -Destination " + BAK, "PASS"),
    ("copy-item 小写", "copy-item " + CFG + " " + BAK, "PASS"),
    ("COPY-ITEM 大写", "COPY-ITEM " + CFG + " " + BAK, "PASS"),
    ("Copy-Item 反斜杠源", "Copy-Item D:" + BS + "myagent" + BS + ".hermes" + BS + "config.yaml " + BAK, "PASS"),
    ("Tee-Object -FilePath 非保护", "Tee-Object -FilePath " + BAK, "PASS"),
    ("Tee-Object 输入位参读", "Tee-Object " + CFG, "PASS"),
    ("内嵌载体源位", 'pwsh -Command "Copy-Item ' + CFG + " " + BAK + '"', "PASS"),
    ("内嵌裸形载体源位", "pwsh -Command Copy-Item " + CFG + " " + BAK, "PASS"),
    ("cmd 载体 copy 源位对照", 'cmd /c "copy ' + CFG + " " + BAK + '"', "PASS"),
])
# ②目标写配置 approve（弹卡）
run("②目标写配置 approve", [
    ("Copy-Item BAK CFG", "Copy-Item " + BAK + " " + CFG, "approve"),
    ("-Destination CFG 命名目标", "Copy-Item " + BAK + " -Destination " + CFG, "approve"),
    ("Tee-Object -FilePath CFG", "Tee-Object -FilePath " + CFG, "approve"),
    ("内嵌 Copy-Item 目标配置", 'pwsh -Command "Copy-Item ' + BAK + " " + CFG + '"', "approve"),
    ("cp 对照同语义", "cp " + BAK + " " + CFG, "approve"),
])
# ③目标写守卫文件/目录（复制族既有口径=approve，与 cp 同款；round10-context §27 PM 裁定）
run("③目标写守卫=cp同款", [
    ("Copy-Item evil HD", "Copy-Item evil " + HD, "approve"),
    ("Copy-Item evil GUARD 无尾斜杠", "Copy-Item evil " + GUARD, "approve"),
    ("Copy-Item evil GUARD/ 尾斜杠", "Copy-Item evil " + GUARD + "/", "approve"),
    ("cp evil GUARD 对照", "cp evil " + GUARD, "approve"),
    ("cp evil GUARD/ 对照", "cp evil " + GUARD + "/", "approve"),
])
# ④Set-Content 族「出现即写」支不回潮（block）
run("④出现即写支不回潮", [
    ("Set-Content CFG", "Set-Content " + CFG + " x", "block"),
    ("Add-Content CFG", "Add-Content " + CFG + " x", "block"),
    ("Out-File CFG", "Out-File " + CFG, "block"),
    ("内嵌 Set-Content", 'pwsh -Command "Set-Content ' + CFG + ' x"', "block"),
    ("out-file 小写", "out-file " + CFG, "block"),
    ("echo x > CFG 直写", "echo x > " + CFG, "block"),
])
# FP 面：非保护目标、读命令
run("FP 负例", [
    ("Copy-Item ws 非保护", "Copy-Item " + WS + " D:/myagent/workspace/b.txt", "PASS"),
    ("Get-Content CFG 读", "Get-Content " + CFG, "PASS"),
    ("cat CFG 读", "cat " + CFG, "PASS"),
    ("Copy-Item -Container CFG -Dest ws", "Copy-Item -Container " + CFG + " -Destination " + WS, "PASS"),
    ("Copy-Item 通配符", "Copy-Item D:/myagent/workspace/*.txt D:/myagent/workspace/backup", "PASS"),
    ("链式 Copy-Item CFG BAK && echo", "Copy-Item " + CFG + " " + BAK + " && echo done", "PASS"),
    ("mv 改名族不拦", "mv " + CFG + " " + BAK, "PASS"),
])
# execute_code 面：内嵌 shell 字符串里的 Copy-Item 源位
print("--- execute_code 面 ---")
code = "import os\nos.system(" + q2 + "pwsh -Command Copy-Item " + CFG + " " + BAK + q2 + ")"
r = h.on_pre_tool_call("execute_code", {"code": code})
print("[ok  ] " if (r or {}).get("action", "PASS") == "PASS" else "[DIFF]", "ec 内嵌源位 ->", (r or {}).get("action", "PASS"))
code2 = "import os\nos.system(" + q2 + "Copy-Item " + BAK + " " + CFG + q2 + ")"
r = h.on_pre_tool_call("execute_code", {"code": code2})
print("[ok  ] " if (r or {}).get("action", "PASS") == "approve" else "[DIFF]", "ec 内嵌目标配置 ->", (r or {}).get("action", "PASS"))
