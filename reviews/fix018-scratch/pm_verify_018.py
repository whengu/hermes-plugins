# pm_verify_018 验收断言（F-17-S1 误拦封堵 + round17 全 19 形零回退复制）
# 接口同 pm_verify_017（on_pre_tool_call terminal）。基线 1bcc8cd 预期:
#   G1/G3/G5/G6/G7 FAIL(-t 目标在 HOME 外，tilde token=源位读被 1f 补点误拦)；其余 ok。
#   0 FAIL=完成。
import importlib.util, os
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
spec = importlib.util.spec_from_file_location("hg", "D:" + B + "myagent" + B + "workspace" + B + "write-guard" + B + "handler.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def call(cmd):
    return m.on_pre_tool_call("terminal", {"command": cmd}, "pm")
def verdict(r):
    return "PASS" if r is None else str(r.get("action"))

H = "~/.hermes"
CFG = "~/.hermes/config.yaml"
# (id, cmd, want)  want: "hit"=弹卡(approve/block 任意), "pass"=放行, 具体串=精确
cases = [
    # ---- G 组：F-17-S1 靶心（-t 目标在 HOME 外 → 尾随 tilde token 是源位读，必须放行）
    ("G1 cp -t D:/other/out ~/.hermes/x.dat evil 源读",   "cp -t D:/other/out ~/.hermes/x.dat evil.bin", "pass"),
    ("G3 cp -t D:/other/out ~/.hermes/config.yaml evil",  "cp -t D:/other/out " + CFG + " evil.bin", "pass"),
    ("G5 rsync -t D:/other/out ~/.hermes/x.dat dest",     "rsync -t D:/other/out " + H + "/x.dat dest.bin", "pass"),
    ("G6 cp -t D:/other/out a.md ~/.hermes/logs b.md",    "cp -t D:/other/out a.md " + H + "/logs b.md", "pass"),
    ("G7 install -t D:/other/out ~/.hermes/x",            "install -t D:/other/out " + H + "/x", "pass"),
    # ---- G 锁：-t 目标在 HOME 内 → 目标位即写，弹卡不回退
    ("G2 cp -t ~/.hermes/out/ 真目标",                     "cp -t ~/.hermes/out/ src1 src2", "hit"),
    ("G4 cp -t ~/.hermes ~/.hermes/config.yaml evil",     "cp -t " + H + " " + CFG + " evil", "hit"),
    ("G8 -t目标HOME内+源也tilde 歧义取拦维持",           "cp -t ~/.hermes/out ~/.hermes/x.dat evil", "hit"),
    # ---- round17 T/K 全 19 形零回退复制
    ("T1 cp evil ~/.hermes/x.dat",                        "cp evil ~/.hermes/x.dat", "hit"),
    ("T2 cp evil ~/.hermes/skills/",                      "cp evil ~/.hermes/skills/", "hit"),
    ("T3 cp evil ~/.hermes/logs",                         "cp evil ~/.hermes/logs", "hit"),
    ("T4 cp evil ~/.hermes 目录本身",                      "cp evil ~/.hermes", "hit"),
    ("T5 cp evil ~/.hermes/y 无扩展",                      "cp evil ~/.hermes/y", "hit"),
    ("T6 cp \"-t~/.hermes/tdir\" x 粘连",                 'cp "-t~/.hermes/tdir" x', "hit"),
    ("T7 bash -c 内 cp evil ~/.hermes/z",                 "bash -c 'cp evil ~/.hermes/z'", "hit"),
    ("T8 cp -t ~/.hermes/x.dat evil 分列目标在HOME",       "cp -t ~/.hermes/x.dat evil", "hit"),
    ("K1 cat ~/.hermes/x.dat 读",                         "cat ~/.hermes/x.dat", "pass"),
    ("K2 mv ~/.hermes/a ~/.hermes/b 双别名",              "mv ~/.hermes/a ~/.hermes/b", "pass"),
    ("K3 mv ~/.hermes/config.yaml out 源位读",            "mv " + CFG + " D:/other/old.cfg", "pass"),
    ("K4 grep -r pattern ~/.hermes/logs",                 "grep -r pattern ~/.hermes/logs", "pass"),
    ("K5 cp ~/.hermes/logs/x.log 源位拷出",           "cp ~/.hermes/logs/x.log D:/other/dst.log", "pass"),
    ("K6 清单文件 tilde 弹卡",                             "cp evil " + CFG, "hit"),
    ("K7 alias 读",                                       "cat " + H + "/plugins/write-guard/handler.py", "pass"),
    ("K8 mv 绝对改名",                                     "mv D:/other/a.txt " + CFG, "hit"),
]
fails = []
for cid, cmd, want in cases:
    r = call(cmd)
    v = verdict(r)
    ok = (v == "PASS") if want == "pass" else (v != "PASS")
    print(("ok  " if ok else "FAIL"), cid, "want=", want, "got=", v, "|", cmd[:64])
    if not ok: fails.append(cid)
print(f"\n===== pm_verify_018: {len(cases) - len(fails)}/{len(cases)} PASS =====")
print("FAILS:", fails or "none")
