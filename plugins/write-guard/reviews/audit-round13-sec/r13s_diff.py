# r13 差分复测：同形集分别跑 r12 基线 handler 与 r13 现网 handler，标 DIFF=回潮 / SAME=既有
import importlib.util, os
os.environ["HERMES_HOME"] = r"D:\myagent\.hermes"
os.chdir(r"D:\myagent\workspace")
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
A = load("wga", r"D:\myagent\workspace\write-guard\reviews\audit-round13-sec\handler_r12.py")
Bm = load("wgb", r"D:\myagent\workspace\write-guard\handler.py")
def act(mod, cmd):
    r = mod.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action") or "PASS"
HOME = "D:/myagent/.hermes"; CFG = HOME + "/config.yaml"; W = "D:/myagent/workspace"
GUARD = HOME + "/plugins/write-guard"; HD = GUARD + "/handler.py"
forms = {
 "G1 cp \"-tGUARD/\"": 'cp evil.txt "-t' + GUARD + '/"',
 "G3 cp \"--td=GUARD\"": 'cp evil.txt "--target-directory=' + GUARD + '"',
 "G4 dd \"of=CFG\"": 'dd "of=' + CFG + '" if=s bs=1 count=4',
 "G5 cp '-t=GUARD'": "cp '-t=" + GUARD + "' evil.txt",
 "G6 install '-tGUARD/'": "install '-t" + GUARD + "/' evil.txt",
 "I1 curl \"--output=CFG\"": 'curl "--output=' + CFG + '" http://x',
 "I2 curl \"-o=CFG\"": 'curl "-o=' + CFG + '" http://x',
 "B1 curl \"-oCFG\"(r13修靶)": 'curl "-o' + CFG + '" http://x',
 "E1 curl \"-soCFG\"(r13修靶)": '"-so' + CFG + '"',
 "X1 CopyItem tgt-first(r13修靶)": "Copy-Item -Destination " + CFG + " -Path " + W + "/x.txt",
 "T1 Tee LiteralPath(r13修靶)": "Tee-Object -LiteralPath " + CFG,
 "K2 锁形 Container CFG-Dest ws": "Copy-Item -Container " + CFG + " -Destination " + W + "/x.txt",
 "K14 curl -O URL": "curl -O http://x/a.zip",
 "X7 cp \"-tGUARD\" no-slash": 'cp handler.py "-t' + GUARD + '"',
 "Z1glue 双连冒号 -Destination:WS -Destination:CFG": "Copy-Item -Destination:" + W + "/a " + " -Destination:" + CFG,
}
for k, c in forms.items():
    a = act(A, c); b = act(Bm, c)
    print(("SAME " if a == b else "DIFF ") + (a + " → " + b).ljust(19), k)
