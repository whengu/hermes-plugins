# round16 验收断言（.hermes 段锚定归一：tilde/$HOME/别名 写旁路靶心 + 读位/红线锁形）
# 基线预期: T1~T6(±T7/T8 视载体展开) FAIL=旁路, K 组 ok。0 FAIL = 完成定义。
import importlib.util, os
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
W = r"D:\myagent\workspace\write-guard"
spec = importlib.util.spec_from_file_location("w", W + B + "handler.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
CFG = "D:" + B + "myagent" + B + ".hermes" + B + "config.yaml"
WS  = "D:" + B + "myagent" + B + "workspace"
def call(cmd):
    r = m.on_pre_tool_call("terminal", {"command": cmd}, "pm")
    return "PASS" if r is None else str(r.get("action"))

cases = [
    # ---- 靶心：tilde/$HOME/别名 写位（基线 PASS=旁路 → 修后 hit）
    ("T1 cp evil ~/.hermes/config.yaml",          "cp evil ~/.hermes/config.yaml", "hit"),
    ("T2 echo > ~/.hermes/config.yaml",           "echo x > ~/.hermes/config.yaml", "hit"),
    ("T3 sed -i ~/.hermes/plugins/wg/handler.py", "sed -i 's/a/b/' ~/.hermes/plugins/write-guard/handler.py", "hit"),
    ("T4 cp \"-t~/.hermes/plugins/wg\" x",        'cp "-t~/.hermes/plugins/write-guard" x', "hit"),
    ("T5 curl \"-o~/.hermes/config.yaml\"",       'curl "-o~/.hermes/config.yaml" url', "hit"),
    ("T6 tee $HOME/.hermes/config.yaml",          "tee $HOME/.hermes/config.yaml", "hit"),
    ("T7 cp %USERPROFILE%\\.hermes\\config.yaml", f"cp evil %USERPROFILE%{B}.hermes{B}config.yaml", "any"),
    ("T8 cp C:/Users/guwh/.hermes/config.yaml",   "cp evil C:/Users/guwh/.hermes/config.yaml", "hit"),
    # ---- 锁形：读位/源位/非 .hermes 零误拦（基线已 PASS，修后不得回退）
    ("K1 cat ~/.hermes/config.yaml 读位",          "cat ~/.hermes/config.yaml", "pass"),
    ("K2 mv ~/.hermes/config.yaml x 源位",         "mv ~/.hermes/config.yaml " + WS + "/x", "pass"),
    ("K3 mv x ~/.hermes/config.yaml 目标覆写",      "mv " + WS + "/x ~/.hermes/config.yaml", "hit"),
    ("K4 cp ~/.hermes-agent/x 前缀名非段",          "cp evil ~/.hermes-agent/config.yaml", "pass"),
    ("K5 echo > ~/.vscode/settings.json 零扰动",    "echo x > ~/.vscode/settings.json", "pass"),
    ("K6 绝对形不回潮",                              f"cp evil {CFG}", "hit"),
    ("K7 cat C:/Users/guwh/.hermes/config.yaml 别名读", "cat C:/Users/guwh/.hermes/config.yaml", "pass"),
    ("K8 绝对 tilde 双写形 cp CFG2 ~/.hermes/x",     f"cp {CFG} ~/.hermes/x.yaml", "hit"),
]
nf = 0
for label, cmd, want in cases:
    got = call(cmd)
    okv = {"hit": got in ("approve", "block"), "pass": got == "PASS", "any": True}[want]
    nf += (not okv)
    print(f"{'ok ' if okv else 'FAIL'} {label:44s} -> {got:8s} want {want}")
print(f"通过 {len(cases)-nf} 失败 {nf} {[] if not nf else '(有失败)'}")
