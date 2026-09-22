# round10 安全路探针 H：F-10-1 证据补全（位置首参/前缀×载体×wrapper）+ F-10-2 修法方向核证（token 独立约束不破坏既有锁形）
import importlib.util, os, re
BS, q2 = chr(92), chr(34)
os.environ["HERMES_HOME"] = "D:" + BS + "myagent" + BS + ".hermes"
os.chdir("D:" + BS + "myagent" + BS + "workspace")
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("hg", os.path.join(HERE, "..", "..", "handler.py"))
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
ospec = importlib.util.spec_from_file_location("ho", os.path.join(HERE, "handler_r9_cbd6301.py"))
ho = importlib.util.module_from_spec(ospec); ospec.loader.exec_module(ho)
HOME = "D:/myagent/.hermes"
CFG = HOME + "/config.yaml"
WS = "D:/myagent/workspace/a.txt"
GUARD = HOME + "/plugins/write-guard"

def act(mod, cmd):
    r = mod.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action", "PASS")

def cmp(tag, cmd):
    print(f"  new={act(h,cmd):7s} old={act(ho,cmd):7s}  {tag} :: {cmd!r}")

print("--- F-10-1 证据补全 ---")
cmp("Tee-Object 位置首参=目标(PS 语义)", "Tee-Object " + CFG + " " + WS)
cmp("wrapper×前置命名目标", "sudo pwsh -Command Copy-Item -Destination " + CFG + " " + WS)
cmp("载体×前置命名目标(裸形)", "pwsh -Command Copy-Item -Destination " + CFG + " " + WS)
cmp("载体引号体内前置", 'pwsh -Command "Copy-Item -Destination ' + CFG + " " + WS + '"')
cmp("锁向对照 尾位命名目标", "Copy-Item " + WS + " -Destination " + CFG)
cmp("锁向对照 cp -t 前缀(cp 已处理)", "cp -t " + CFG + " " + WS)
cmp("Tee-Object -FilePath 前置 载体内", 'pwsh -Command "Tee-Object -FilePath ' + CFG + ' -InputObject x"')

print("--- F-10-2 修法方向：token 独立约束后的锁形预演（模拟候选正则） ---")
CAND = re.compile(r"(?:--output-document|--output|(?:^|(?<=\s))[-/]o|(?:^|(?<=\s))[-/]O)\s*(?:=\s*)?$", re.IGNORECASE)
tests = [
    ("curl -o ", "block 锁保持"),
    ("wget -O ", "block 锁保持"),
    ("sort /O ", "block 锁保持"),
    ("sort -O ", "block 锁保持"),
    ("sort /o ", "block 锁保持"),
    ("curl --output ", "block 锁保持"),
    ("curl http://x/o ", "PASS 期望(FP 修掉)"),
    ("sort D:/myagent/workspace/o ", "PASS 期望(FP 修掉)"),
    ("sort D:/myagent/workspace/my-dir-o ", "PASS 期望(dash 同根旧 FP 顺带)"),
    ("curl -sSL -o ", "block 锁保持"),
]
for before, note in tests:
    print(f"  cand_match={bool(CAND.search(before.rstrip()))!s:5s}  [{note}]  before={before!r}")
# =形链不经过 _OUTPUT_FLAG_RE（走 _OUTPUT_FLAG_EQ_RE/_GLUED_O_RE），锁形 curl -o = CFG：
seg = "curl -o = " + CFG + " http://x"
print("  'curl -o = CFG' 现行为:", act(h, seg), "(r9 锁形，修法不得回退)")
