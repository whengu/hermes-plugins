import importlib.util, os, sys
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
W = r"D:\myagent\workspace\write-guard"
spec = importlib.util.spec_from_file_location("wg", W + B + "handler.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
CFG = "D:" + B + "myagent" + B + ".hermes" + B + "config.yaml"
CFGS = CFG.replace(B, "/")
HD = "D:" + B + "myagent" + B + ".hermes" + B + "plugins" + B + "write-guard" + B + "handler.py"
WSX = "D:/myagent/workspace/x.txt"
def j(cmd):
    r = m._judge_terminal(cmd, "terminal")
    return "PASS" if r is None else str(r.get("action"))
fails = []
def chk(name, cmd, want):
    got = j(cmd)
    ok = got in want
    print(("ok  " if ok else "FAIL"), name, "->", got, "want", "/".join(want))
    if not ok: fails.append(name)
# —— 新封堵（round13 修复目标）——
chk("X1 -Destination CFG -Path ws", "Copy-Item -Destination " + CFGS + " -Path " + WSX, ("approve","block"))
chk("X2 -Destination CFG -LiteralPath ws", "Copy-Item -Destination " + CFGS + " -LiteralPath " + WSX, ("approve","block"))
chk("X3 -Destination:CFG -Path ws 冒号", "Copy-Item -Destination:" + CFGS + " -Path " + WSX, ("approve","block"))
chk("X4 -Destination CFG -Container ws", "Copy-Item -Destination " + CFGS + " -Container " + WSX, ("approve","block"))
chk("T1 Tee -LiteralPath CFG", "Tee-Object -LiteralPath " + CFGS, ("approve","block"))
chk("T2 Tee -LiteralPath:CFG 冒号", "Tee-Object -LiteralPath:" + CFGS, ("approve","block"))
chk("T3 Tee -InputObject x -LiteralPath CFG", "Tee-Object -InputObject x -LiteralPath " + CFGS, ("approve","block"))
chk("E1 curl \"-so CFG\" 引号粘连", 'curl "-so' + CFGS + '" http://x', ("block",))
chk("E2 curl '-o CFG' 单引号粘连", "curl '-o" + CFGS + "' http://x", ("block",))
chk("E3 curl \"-o CFG\" 双引号粘连", 'curl "-o' + CFGS + '" http://x', ("block",))
chk("E4 curl \"-o 守卫源码\"", 'curl "-o' + HD + '" http://x', ("block",))
# —— 锁形保全（现值不得回退）——
chk("K1 -Destination CFG 位置参(r11)", "Copy-Item -Destination " + CFGS + " " + WSX, ("approve","block"))
chk("K2 -Container CFG -Destination ws(r10 B)", "Copy-Item -Container " + CFGS + " -Destination " + WSX, ("PASS",))
chk("K3 -Path CFG -Destination ws(r11 c3)", "Copy-Item -Path " + CFGS + " -Destination " + WSX, ("PASS",))
chk("K4 -Destination ws -Path CFG(r12 c1)", "Copy-Item -Destination " + WSX + " -Path " + CFGS, ("PASS",))
chk("K5 -Path CFG ws 尾位(r12 c5)", "Copy-Item -Path " + CFGS + " " + WSX, ("PASS",))
chk("K6 -Path ws -Destination CFG(r12 X8)", "Copy-Item -Path " + WSX + " -Destination " + CFGS, ("approve","block"))
chk("K7 ws -Destination CFG 末位(r12 X9)", "Copy-Item " + WSX + " -Destination " + CFGS, ("approve","block"))
chk("K8 Tee -FilePath CFG x(r12 T4)", "Tee-Object -FilePath " + CFGS + " x", ("approve","block"))
chk("K9 Tee -FilePath ws 源位", "Tee-Object -FilePath " + WSX + " -Append", ("PASS",))
chk("K10 -Destination:\"CFG\" 引号值(r12 N6)", 'Copy-Item -Destination:"' + CFGS + '" ' + WSX, ("approve","block"))
chk("K11 -Destination ws CFG 反向(r11 m)", "Copy-Item -Destination " + WSX + " " + CFGS, ("PASS",))
chk("K12 pwsh 载体 -Destination CFG(k形)", 'pwsh -Command "Copy-Item -Destination ' + CFGS + " " + WSX + '"', ("approve","block"))
chk("K13 grep \"-o\" 门外(r12 b4)", 'grep "-o" ' + CFGS, ("PASS",))
chk("K14 curl -O URL 红线", "curl -O http://x/a.zip", ("PASS",))
chk("K15 sort ws/o F-10-2 归正", "sort D:/myagent/workspace/o " + CFGS, ("PASS",))
chk("K16 curl -so CFG 无引号(r12 d1)", "curl -so " + CFGS + " http://x", ("block",))
chk("K17 curl -oCFG 粘连(S-1)", "curl -o" + CFGS + " http://x", ("block",))
chk("K18 curl -sfo=CFG 等号(cluster)附录", "curl -sfo=" + CFGS + " http://x", ("PASS",))
chk("K19 curl \"-o\" CFG 引号选项词(r12 b1)", 'curl "-o" ' + CFGS + " http://x", ("block",))
print("通过", 30 - len(fails), "失败", len(fails), fails)
sys.exit(1 if fails else 0)
