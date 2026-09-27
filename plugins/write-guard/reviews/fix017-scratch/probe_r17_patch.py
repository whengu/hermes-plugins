# 定演：h_patch.py（终审猴补丁代跑）跑 pm_verify_017 全 19 形 → 验证 5 点接视图覆盖度
import importlib.util, os
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
spec = importlib.util.spec_from_file_location("p", r"D:\myagent\workspace\write-guard\_r2tmp\r16_audit\h_patch.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
H = "D:" + B + "myagent" + B + ".hermes"
def call(cmd):
    return m.on_pre_tool_call("terminal", {"command": cmd}, "pm")
def verdict(r):
    return "PASS" if r is None else str(r.get("action"))
cases = [
    ("T1", "cp evil ~/.hermes/x.dat", "hit"),
    ("T2", "cp evil ~/.hermes/skills/", "hit"),
    ("T3", "cp evil ~/.hermes/logs", "hit"),
    ("T4", "cp evil ~/.hermes", "hit"),
    ("T5", "cp evil ~/.hermes/y", "hit"),
    ("T6", 'cp "-t~/.hermes/tdir" x', "hit"),
    ("T7", "bash -c 'cp evil ~/.hermes/z'", "hit"),
    ("T8", "cp -t ~/.hermes/x.dat evil", "hit"),
    ("K1", "cat ~/.hermes/x.dat", "pass"),
    ("K2", "mv ~/.hermes/a ~/.hermes/b", "pass"),
    ("K3", "mv ~/.hermes/config.yaml x", "pass"),
    ("K4", "cp evil ~/.hermes-agent/x", "pass"),
    ("K5", "cp evil D:/other/x", "pass"),
    ("K6", "ls ~/.hermes", "pass"),
    ("K7", "cp ~/.hermes/config.yaml D:/tmpd/d.yaml", "pass"),
    ("K8", "echo x > ~/.hermes/note.md", "pass"),
    ("K9", f"cp evil {H}/x.dat", "hit"),
]
nf = 0
for lbl, cmd, want in cases:
    got = verdict(call(cmd))
    ok = got in ("approve", "block") if want == "hit" else got == "PASS"
    nf += (not ok)
    print(f"{'ok ' if ok else 'FAIL'} {lbl:3s} {cmd[:44]:46s} -> {got}")
print("h_patch 判定形 失败", nf)
# 文案现形
r = call(f"cp a.md {H}/skills/safe-config-modify")
print("M-msg:", r.get("message"))
