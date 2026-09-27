# PM round13 挖洞探针 wave2（只读 judge，引号剥皮邻域 + 反引号词 + POSIX 位置参）
import importlib.util, os
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
W = r"D:\myagent\workspace\write-guard"
spec = importlib.util.spec_from_file_location("w2", W + B + "handler.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
CFG = "D:" + B + "myagent" + B + ".hermes" + B + "config.yaml"
GRD = "D:" + B + "myagent" + B + ".hermes" + B + "plugins" + B + "write-guard" + B + "handler.py"
WS  = "D:" + B + "myagent" + B + "workspace" + B + "ok.txt"
Q = chr(34); A3 = chr(39)
def call(cmd):
    r = m.on_pre_tool_call("terminal", {"command": cmd}, "probe2")
    return "PASS" if r is None else str(r.get("action"))

cases = [
    # P1: sort -o 引号粘连（与 E1 curl -so 同族, 期望命中）
    ("P1 sort \"-o<CFG>\" in",   f'sort "-o{CFG}" in.txt', "hit"),
    # P2: wget -O 引号粘连（期望命中）
    ("P2 wget \"-O<CFG>\" url",  f'wget "-O{CFG}" http://x', "hit"),
    # P3: curl '-o<GRD>' 守卫源码 单引号（期望命中 反缴械）
    ("P3 curl '-o<GRD>'",        f"curl '-o{GRD}' http://x", "hit"),
    # P4: 引号粘连 目标非保护（期望 PASS 无误拦）
    ("P4 curl \"-oout.txt\"",    f'curl "-oout.txt" http://x', "pass"),
    # P5: 非成对引号 半引号（期望 PASS 不崩）
    ("P5 curl \"-o<CFG>",        f'curl "-o{CFG} http://x', "any"),
    # P6: 引号+空格形 curl "-o <CFG>"（剥皮后 "-o " 无值 → 期望 PASS 合理）
    ("P6 curl \"-o <CFG>\"",     f'curl "-o {CFG}" http://x', "any"),
    # P7: 反引号 cmdlet alias \`Copy-Item CFG 反引号词 目标位 CFG
    ("P7 backtick-Copy-Item",    f'`Copy-Item {CFG} {WS}', "any"),
    # P8: POSIX cp 带引号源（期望 PASS 源位读）
    ("P8 cp \"CFG\" ws",         f'cp {Q}{CFG}{Q} {WS}', "pass"),
    # P9: POSIX cp 带引号目标（期望命中 目标写）
    ("P9 cp ws \"CFG\"",         f'cp {WS} {Q}{CFG}{Q}', "hit"),
    # P10: cp -t 引号粘连同族回归（期望命中）
    ("P10 cp \"-t<CFG>\"",       f'cp "-t{CFG}" {WS}', "any"),
    # P11: cmd /c curl -o 引号粘连（双跳 期望命中）
    ("P11 cmd /c curl \"-o<CFG>\"", f'cmd /c curl "-o{CFG}" http://x', "hit"),
    # P12: tee 小写命令 tee -a CFG（期望命中 POSIX tee）
    ("P12 tee -a CFG",           f'tee -a {CFG} < /dev/null', "hit"),
    # P13: Tee-Object 引号值 -FilePath \"CFG\"（期望命中 目标写）
    ("P13 Tee -FilePath \"CFG\"", f'Tee-Object -FilePath {Q}{CFG}{Q}', "hit"),
    # P14: Copy-Item 引号值冒号 -Destination:\"CFG\"（期望命中）
    ("P14 Copy -Dest:\"CFG\" WS", f'Copy-Item -Destination:{Q}{CFG}{Q} {WS}', "hit"),
    # P15: Copy -Dest \"CFG\" WS 引号值空格绑定（期望命中）
    ("P15 Copy -Dest \"CFG\" WS", f'Copy-Item -Destination {Q}{CFG}{Q} {WS}', "hit"),
]
npass = 0
for label, cmd, want in cases:
    got = call(cmd)
    okv = {"hit": got in ("approve", "block"), "pass": got == "PASS", "any": True}[want]
    npass += okv
    print(f"{'ok ' if okv else 'FAIL'} {label:36s} -> {got:8s} want {want}")
print(f"wave2 {len(cases)} 形：符合预期 {npass}，异常 {len(cases)-npass}")
