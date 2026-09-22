import importlib.util, os, sys
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
W = r"D:\myagent\workspace\write-guard"
CFG = "D:" + B + "myagent" + B + ".hermes" + B + "config.yaml"
CFGS = CFG.replace(B, "/")
HD = "D:" + B + "myagent" + B + ".hermes" + B + "plugins" + B + "write-guard" + B + "handler.py"
WSX = "D:/myagent/workspace/x.txt"

def load(p, name):
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

old = load(W + B + "_r2tmp" + B + "r13q" + B + "h_4e254c8.py", "oldw")
new = load(W + B + "handler.py", "neww")

def j(m, cmd):
    r = m._judge_terminal(cmd, "terminal")
    return "PASS" if r is None else str(r.get("action"))

FORMS = [
    # (name, cmd, expected_new)
    ("X1", "Copy-Item -Destination " + CFGS + " -Path " + WSX, "approve"),
    ("X2", "Copy-Item -Destination " + CFGS + " -LiteralPath " + WSX, "approve"),
    ("X3", "Copy-Item -Destination:" + CFGS + " -Path " + WSX, "approve"),
    ("X4", "Copy-Item -Destination " + CFGS + " -Container " + WSX, "approve"),
    ("T1", "Tee-Object -LiteralPath " + CFGS, "approve"),
    ("T2", "Tee-Object -LiteralPath:" + CFGS, "approve"),
    ("T3", "Tee-Object -InputObject x -LiteralPath " + CFGS, "approve"),
    ("E1", 'curl "-so' + CFGS + '" http://x', "block"),
    ("E2", "curl '-o" + CFGS + "' http://x", "block"),
    ("E3", 'curl "-o' + CFGS + '" http://x', "block"),
    ("E4", 'curl "-o' + HD + '" http://x', "block"),
    ("Z1", "Copy-Item -Destination " + CFGS + " -Destination " + WSX, "PASS"),
    ("Z2", "Copy-Item -Destination " + WSX + " -Destination " + CFGS, "approve"),
    ("Z3", "Tee-Object -FilePath " + WSX + " -LiteralPath " + CFGS, "PASS"),
    ("N1 copy dest 空格引号值", 'Copy-Item -Destination "' + CFGS + '" ' + WSX, "approve"),
    ("N2 tee FP 空格引号值", 'Tee-Object -FilePath "' + CFGS + '"', "approve"),
    ("N3 tee FP冒号引号值", 'Tee-Object -FilePath:"' + CFGS + '"', "approve"),
    ("N4 tee LP冒号(r12漏)", "Tee-Object -LiteralPath:" + CFGS, "approve"),
    ("N5 copy LP 源参引号", 'Copy-Item -LiteralPath "' + CFGS + '" ' + WSX, "PASS"),
    ("P1 pwsh载体 X1", 'pwsh -Command "Copy-Item -Destination ' + CFGS + " -Path " + WSX + '"', "approve"),
    ("P2 pwsh载体 T1", 'pwsh -Command "Tee-Object -LiteralPath ' + CFGS + '"', "approve"),
    ("P3 sudo pwsh载体 T1", 'sudo pwsh -Command "Tee-Object -LiteralPath ' + CFGS + '"', "approve"),
    ("P4 posix位参 Copy-Item", "Copy-Item " + WSX + " " + CFGS, "approve"),
    ("P5 Copy-Item CFG 源位", "Copy-Item " + CFGS + " " + WSX, "PASS"),
    ("P6 tee 混合大写", "Tee-Object -LiteralPath " + CFGS + " -Append", "approve"),
    ("P7 copy 双标志目标在前(K2)", "Copy-Item -Container " + CFGS + " -Destination " + WSX, "PASS"),
    ("P8 curl -o 空格引号值", 'curl -o "' + CFGS + '" http://x', "block"),
    ("Q1 sort 引号粘连(-oF)", 'sort "-o' + CFGS + '" d.txt', "block"),
    ("Q2 curl 引号header负例", 'curl "-H" "X-O: v" http://x ' + CFGS, "PASS"),
    ("Q3 curl 引号-oL负例", 'curl "-oL" http://x', "PASS"),
    ("Q4 copy族引号粘连-t(登记)", 'cp "-t' + CFG.replace(B, "/") + '" src', "PASS"),
    ("K13 grep门外", 'grep "-o" ' + CFGS, "PASS"),
    ("K14 curl -O URL", "curl -O http://x/a.zip", "PASS"),
    ("K18 等号附录", "curl -sfo=" + CFGS + " http://x", "PASS"),
    ("R1 gateway restart 红线", "hermes gateway restart", "block"),
    ("R2 cp 写配置 红线", "cp evil " + CFGS, "approve"),
    ("R3 cat 配置 读", "cat " + CFGS, "PASS"),
    ("R4 curl -o 守卫源码(S-1旧)", "curl -o" + HD + " http://x", "block"),
]
print(f"{'form':38s} {'old(r12)':9s} {'new(r13)':9s} {'want':8s} verdict")
ndiff = 0
for name, cmd, want in FORMS:
    try: o = j(old, cmd)
    except Exception as e: o = "ERR:" + type(e).__name__
    try: n = j(new, cmd)
    except Exception as e: n = "ERR:" + type(e).__name__
    ok = "OK" if n in (want, "block") and (want == "approve" or n == want) else "**MISMATCH**"
    flip = "FLIP" if o != n else "    "
    if o != n: ndiff += 1
    print(f"{name:38s} {o:9s} {n:9s} {want:8s} {flip} {ok}")
print("generation diffs:", ndiff, "/", len(FORMS))
