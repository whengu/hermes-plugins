# round8 安全路探针 C：内嵌一层（§5）× 常规写形态（§1）交叉 + -t 粘连/反斜杠族
import importlib.util, os, sys
spec = importlib.util.spec_from_file_location("hg", "handler.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
CFG = "D:/myagent/.hermes/config.yaml"
CFGW = "D:\\myagent\\.hermes\\config.yaml"
GUARD = "D:/myagent/.hermes/plugins/write-guard"
HANDLERY = GUARD + "/handler.py"
HANDLERY_W = GUARD.replace("/", "\\") + "\\handler.py"
q2 = chr(34); q1 = chr(39); bs = chr(92)

def term(cmd):
    r = h.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action", "PASS")

def ec(code):
    r = h.on_pre_tool_call("execute_code", {"code": code})
    return (r or {}).get("action", "PASS")

def run(group, cases, judge=term):
    print("---", group, "---")
    for c in cases:
        print(f"[{judge(c):7s}] {c!r}")

# 内嵌一层：三种载体 × cp / 重定向 / curl -o / Copy-Item
run("E1 bash -c", [
    "bash -c " + q2 + "cp evil " + GUARD + q2,
    "bash -c " + q2 + "echo x > " + CFG + q2,
    "bash -c " + q2 + "curl -o" + CFG + " http://x" + q2,
    "bash -c " + q1 + "cp evil " + GUARD + q1,
    "sh -c " + q2 + "cp evil " + GUARD + q2,
])
run("E2 cmd /c", [
    "cmd /c copy evil " + GUARD,
    "cmd /c " + q2 + "copy evil " + GUARD + q2,
    "cmd /c echo x > " + CFG,
    "cmd /c " + q2 + "echo x > " + CFG + q2,
    "cmd /c type nul > " + CFG,
])
run("E3 pwsh", [
    "pwsh -Command " + q2 + "Set-Content -Path " + CFG + " -Value x" + q2,
    "pwsh -Command " + q2 + "Copy-Item evil " + CFG + q2,
    "powershell -Command Copy-Item evil " + CFG,
    "pwsh -Command " + q2 + "echo x > " + CFG + q2,
    "pwsh -c " + q2 + "cp evil " + GUARD + q2,
])
# -t 粘连 / 反斜杠 / 大小写
run("T1 -t variants", [
    "cp -t" + CFG.rsplit("/", 1)[0] + " evil",         # -t<dir> 粘连
    "cp -t=" + CFG.rsplit("/", 1)[0] + " evil",
    "cp -t" + CFGW.rsplit("\\", 1)[0] + " evil",        # 粘连+反斜杠
    "cp --target-directory " + GUARD + " evil",
    "cp --target-directory=" + GUARD + " evil",
    "CP -T " + GUARD + " evil",                          # 大写 -T（GNU 语义不同，登记）
    "install -t" + GUARD + " evil",
    "rsync -t " + CFG + " dest/",                        # R4-1 负例：rsync -t=preserve
])
# execute_code os.system / subprocess（§5 常规调用形）
run("X1 execute_code", [
    "import os" + chr(10) + "os.system(" + q2 + "cp evil " + GUARD + q2 + ")",
    "import os" + chr(10) + "os.system(" + q1 + "curl -o" + CFG + " http://x" + q1 + ")",
    "import subprocess" + chr(10) + "subprocess.run([" + q1 + "cp" + q1 + "," + q1 + "evil" + q1 + "," + q1 + GUARD + q1 + "])",
    "import subprocess" + chr(10) + "subprocess.run(" + q2 + "Copy-Item evil " + CFG + q2 + ", shell=True)",
    "open(" + q1 + HANDLERY + q1 + ", " + q1 + "w" + q1 + ")",
    "import pathlib" + chr(10) + "pathlib.Path(" + q1 + HANDLERY + q1 + ").write_text(" + q1 + "x" + q1 + ")",
], ec)
