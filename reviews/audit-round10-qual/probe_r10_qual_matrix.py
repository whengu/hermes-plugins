# round10 质量路终审探针（只读）：F-9-1 并入 _COPY_CMDS 连带面矩阵 + 红线正确入口
# 期望标注：PASS=无处置放行；approve=弹卡；block=截断
import importlib.util, os, sys
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
spec = importlib.util.spec_from_file_location("wg", r"D:" + B + "myagent" + B + "workspace" + B + "write-guard" + B + "handler.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

CFG   = "D:" + B + "myagent" + B + ".hermes" + B + "config.yaml"
CFGS  = CFG.replace(B, "/")
HAND  = "D:" + B + "myagent" + B + ".hermes" + B + "plugins" + B + "write-guard" + B + "handler.py"
HANDS = HAND.replace(B, "/")
GD    = "D:" + B + "myagent" + B + ".hermes" + B + "plugins" + B + "write-guard"
GDS   = GD.replace(B, "/")
GDST  = GD + B                                    # 无尾分隔符目录形（F-1 面）
WS    = "D:" + B + "myagent" + B + "workspace"
WSS   = WS.replace(B, "/")
E1    = WSS + "/x1.txt"
E2    = WSS + "/x2.txt"

def via_terminal(cmd):
    r = m.on_pre_tool_call("terminal", {"command": cmd}, task_id="qual-r10")
    if r is None: return "PASS"
    return str(r.get("action"))

CASES = [
 # ---- 名实对读关键例 ----
 ("M-01 Copy-Item 非保护目标(e->w)",          f"Copy-Item {CFGS} {E1}",                 "PASS"),
 ("M-02 Copy-Item 目标写守卫handler.py(报告称block)", f"Copy-Item {E1} {HANDS}",        "approve"),
 ("M-03 Copy-Item 目标守卫目录带尾分隔符",     f"Copy-Item {E1} {GDS}/",                  "approve"),
 ("M-04 Copy-Item 目标守卫目录无尾分隔符(F-1形)", f"Copy-Item {E1} {GDS}",               "approve"),
 ("M-05 Copy-Item -Destination CFGS",         f"Copy-Item {E1} -Destination {CFGS}",     "approve"),
 ("M-06 Copy-Item -Path CFGS -Destination E1",f"Copy-Item -Path {CFGS} -Destination {E1}","PASS"),
 ("M-07 Copy-Item -Recurse GD CFGS(目标写配置)", f"Copy-Item -Recurse {GDS} {CFGS}",     "approve"),
 ("M-08 Copy-Item -Recurse -Destination GD",   f"Copy-Item -Recurse {CFGS} -Destination {GDS}","approve"),
 ("M-09 Copy-Item 大写目标CFG 非保护源",       f"Copy-Item {E1} {CFG}",                  "approve"),
 ("M-10 cp -r 目标守卫handler(对照零分叉)",     f"cp -r {E1} {HANDS}",                    "approve"),
 ("M-11 Tee-Object -FilePath CFG(单参)",       f"Tee-Object -FilePath {CFGS}",           "approve"),
 ("M-12 Tee-Object -Append CFG",               f"Tee-Object -Append {CFGS}",             "approve"),
 ("M-13 Tee-Object -FilePath E1(非保护)",      f"Tee-Object -FilePath {E1}",             "PASS"),
 ("M-14 Tee-Object evil CFG(双位参末位)",      f"Tee-Object {E1} {CFGS}",                "approve"),
 ("M-15 pwsh载体 Copy-Item evil CFGS",         f'pwsh -Command "Copy-Item evil {CFGS}"', "approve"),
 ("M-16 cmd /c copy evil CFGS(既有族)",         f"cmd /c copy {E1} {CFGS}",               "approve"),
 ("M-17 Copy-Item 源位CFG+Destination非保护",   f"Copy-Item -LiteralPath {CFGS} -Destination {E2}","PASS"),
 ("M-18 bash载体 cp evil GD(通道)",             f'bash -c "cp evil {GDS}"',               "approve"),
 ("M-19 Set-Content CFG(出现即写支不回潮)",     f"Set-Content {CFGS} x",                  "block"),
 ("M-20 Copy-Item 守卫源→非保护目标(红线复制不拦)", f"Copy-Item {HANDS} {E1}",            "PASS"),
 ("M-21 tee 非保护目标(既有F-9-4负例)",         f"cat x | tee {WSS}/t.log",               "PASS"),
 ("M-22 cp CFG BAK(对照源位读)",               f"cp {CFGS} {WSS}/bak.yaml",              "PASS"),
]

fail = 0
for name, cmd, exp in CASES:
    got = via_terminal(cmd)
    tag = "OK " if got == exp else "DRIFT"
    if got != exp: fail += 1
    print(f"{tag:6s} {name:48s} exp={exp:8s} got={got}")
print("---")
print("矩阵例数:", len(CASES), " 漂移:", fail)

# 红线正确入口（on_pre_tool_call）抽查
print("== 红线入口抽查 ==")
for name, cmd in [
    ("gateway restart 直写", "hermes gateway restart"),
    ("gateway bs+LF 续行", "hermes gateway " + chr(92) + chr(10) + "restart"),
    ("gateway status 不误伤", "hermes gateway status"),
    ("restart 词孤现", "systemctl restart nginx"),
]:
    print(f"  {name:24s} -> {via_terminal(cmd)}")
