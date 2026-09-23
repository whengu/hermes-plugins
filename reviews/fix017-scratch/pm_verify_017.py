# pm_verify_017 验收断言（F-16-S1 宽拦族 tilde 封堵 8 靶心 + 零误拦锁 9 + 文案 2）
# 基线 70948f8 预期: T 组 FAIL(=tilde 旁路), K 组 ok, M 组文案断言(修前=旧句 FAIL)。0 FAIL=完成。
import importlib.util, os
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
spec = importlib.util.spec_from_file_location("w", r"D:\myagent\workspace\write-guard" + B + "handler.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
H = "D:" + B + "myagent" + B + ".hermes"
def call(cmd):
    r = m.on_pre_tool_call("terminal", {"command": cmd}, "pm")
    return r
def verdict(r):
    return "PASS" if r is None else str(r.get("action"))
def msg_of(r):
    return "" if r is None else str(r.get("message", ""))

cases = [
    # 靶心：cp 宽拦族 tilde 形（基线 PASS=旁路 → 修后 hit）
    ("T1 cp evil ~/.hermes/x.dat",          "cp evil ~/.hermes/x.dat", "hit", None),
    ("T2 cp evil ~/.hermes/skills/",        "cp evil ~/.hermes/skills/", "hit", None),
    ("T3 cp evil ~/.hermes/logs",           "cp evil ~/.hermes/logs", "hit", None),
    ("T4 cp evil ~/.hermes 目录本身",         "cp evil ~/.hermes", "hit", None),
    ("T5 cp evil ~/.hermes/y 无扩展",         "cp evil ~/.hermes/y", "hit", None),
    ("T6 cp \"-t~/.hermes/tdir\" x 粘连",    'cp "-t~/.hermes/tdir" x', "hit", None),
    ("T7 bash -c 内 cp evil ~/.hermes/z",    "bash -c 'cp evil ~/.hermes/z'", "hit", None),
    ("T8 cp evil ~/.hermes/x.dat -t形分列",   "cp -t ~/.hermes/x.dat evil", "hit", None),
    # 锁：读/源/改名/零扰动 全保持
    ("K1 cat ~/.hermes/x.dat 读",            "cat ~/.hermes/x.dat", "pass", None),
    ("K2 mv ~/.hermes/a ~/.hermes/b 改名",    "mv ~/.hermes/a ~/.hermes/b", "pass", None),
    ("K3 mv ~/.hermes/config.yaml x 源读",   "mv ~/.hermes/config.yaml x", "pass", None),
    ("K4 cp evil ~/.hermes-agent/x 前缀名",   "cp evil ~/.hermes-agent/x", "pass", None),
    ("K5 cp evil D:/other/x HOME外",          "cp evil D:/other/x", "pass", None),
    ("K6 ls ~/.hermes 读",                    "ls ~/.hermes", "pass", None),
    ("K7 cp ~/.hermes/config.yaml dest 源读", "cp ~/.hermes/config.yaml D:/tmpd/d.yaml", "pass", None),
    ("K8 echo x > ~/.hermes/note.md 清单外",   "echo x > ~/.hermes/note.md", "pass", None),
    ("K9 绝对 cp <H>/x.dat 不回退",            f"cp evil {H}/x.dat", "hit", None),
    # 文案断言（用户可解释性要求）：宽拦场景消息须自解释
    ("M1 cp 目录目标 文案含 落位/两跳 不含谎称配置文件",
        f"cp a.md {H}/skills/safe-config-modify", "hit", "wideblock"),
    ("M2 真配置面 文案保持 配置文件 句",
        f"cp a {H}/config.yaml", "hit", "config"),
]
nf = 0
for label, cmd, want, msgchk in cases:
    r = call(cmd)
    got = verdict(r)
    okv = {"hit": got in ("approve", "block"), "pass": got == "PASS"}[want]
    if okv and msgchk:
        msg = msg_of(r)
        if msgchk == "wideblock":
            okv = ("两跳" in msg or "落位" in msg) and ("受保护的 Hermes 配置文件" not in msg)
        elif msgchk == "config":
            okv = "配置文件" in msg
    nf += (not okv)
    print(f"{'ok ' if okv else 'FAIL'} {label:44s} -> {got}")
print(f"通过 {len(cases)-nf} 失败 {nf}")
