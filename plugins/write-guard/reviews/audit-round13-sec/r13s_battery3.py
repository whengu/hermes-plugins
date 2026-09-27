# r13 差分复测第3批：实机可写形 × 判定端对拍（限定 workspace 内假目标同构，不触 .hermes）
import importlib.util, os
os.environ["HERMES_HOME"] = r"D:\myagent\.hermes"
os.chdir(r"D:\myagent\workspace")
spec = importlib.util.spec_from_file_location("wg", r"D:\myagent\workspace\write-guard\handler.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
def act(cmd):
    r = h.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action") or "PASS"
GUARD = "D:/myagent/.hermes/plugins/write-guard"
HOME  = "D:/myagent/.hermes"
CFG   = HOME + "/config.yaml"
W     = "D:/myagent/workspace"
cases = {
 # 实机活证真写(P1..P4/P7/P8=真、curl=等号死选项不立项) × 判定端
 "G1 cp evil \"-tGUARD/\" (P1真写形)": act('cp evil.txt "-t' + GUARD + '/"'),
 "G2 cp evil '-tGUARD/'": act("cp evil.txt '-t" + GUARD + "/'"),
 "G3 cp evil \"--target-directory=GUARD\" (P3真写)": act('cp evil.txt "--target-directory=' + GUARD + '"'),
 "G4 dd \"of=CFG\" if=x (P4真写)": act('dd "of=' + CFG + '" if=src.txt bs=1 count=4'),
 "G5 cp \'-t=<GUARD>\' evil (P8真写形)": act("cp '-t=" + GUARD + "' evil.txt"),
 "G6 install '-tGUARD/' evil (W5真写形)": act("install '-t" + GUARD + "/' evil.txt"),
 # 同形裸对照锚（必须命中=证明拦截面在，引号是唯一切换量）
 "H1 bare cp \"-tGUARD\" -> 已拦?": act("cp evil.txt -t" + GUARD),
 "H2 bare cp --target-directory=GUARD": act("cp evil.txt --target-directory=" + GUARD),
 "H3 bare dd of=CFG": act("dd of=" + CFG + " if=src.txt bs=1 count=4"),
 "H4 cp '-t' GUARD split (F-7-2 登记面)": act("cp '-t' " + GUARD + " evil.txt"),
 # curl 等号引号形（活证=死选项，期望 PASS=与语义一致，不得误拦）
 "I1 curl \"--output=CFG\" (活证未知选项)": act('curl "--output=' + CFG + '" http://x'),
 "I2 curl \"-o=CFG\" (活证 exit=3)": act('curl "-o=' + CFG + '" http://x'),
 # wget -O 引号粘连（wget 语义 -o=logfile / -O=output；活证缺失=登记疑问项不立项）
 "J1 wget \"-O<CFG>\" url": act('wget "-O' + CFG + '" http://x'),
 "J2 wget \"-o<CFG>\" url": act('wget "-o' + CFG + '" http://x'),
}
for k, v in cases.items(): print(v.ljust(9), k)
