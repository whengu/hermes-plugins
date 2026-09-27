# round11 安全路探针 E：新旁路候选族精细复测（F-11-1/2/3/4 证据链）+ r9/r10 代际对照
import importlib.util, os
BS, q1, q2 = chr(92), chr(39), chr(34)
os.environ["HERMES_HOME"] = "D:" + BS + "myagent" + BS + ".hermes"
os.chdir("D:" + BS + "myagent" + BS + "workspace")
HERE = os.path.dirname(os.path.abspath(__file__))

def load(tag, path):
    spec = importlib.util.spec_from_file_location(tag, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

new = load("hn", os.path.join(HERE, "..", "..", "handler.py"))
r10 = load("r10", os.path.join(HERE, "..", "audit-round10-qual", "base", "handler_r10commit.py"))
r9 = load("r9", os.path.join(HERE, "..", "audit-round10-sec", "handler_r9_cbd6301.py"))

HOME = "D:/myagent/.hermes"
CFG = HOME + "/config.yaml"
WS = "D:/myagent/workspace/a.txt"
BAK = "D:/myagent/workspace/bak.yaml"

def act(mod, cmd):
    r = mod.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action") or "PASS"

def run(group, cases):
    print("---", group, "---")
    for tag, cmd in cases:
        n, o10, o9 = act(new, cmd), act(r10, cmd), act(r9, cmd)
        print(f"new={n:8s} r10={o10:8s} r9={o9:8s} | {tag} :: {cmd!r}")

# F-11-4：o 收尾 cluster + 空格值（pwsh/curl 真写已活证：curl -so 实际下载成功）
run("F-11-4 o尾cluster 空格值", [
    ("curl -so CFG 空格", "curl -so " + CFG + " http://x"),
    ("curl -sSLfo CFG", "curl -sSLfo " + CFG + " http://x"),
    ("sort -ro CFG", "sort -ro " + CFG + " d.txt"),
    ("wget -qO CFG", "wget -qO " + CFG + " http://x"),
    ("误拦对照 curl -so WS 非保护", "curl -so " + WS + " http://x"),
    ("对照 cluster 尾非o: -sL 独立", "curl -sL -o " + CFG + " http://x"),
])
# F-11-2：引号包选项词（boundary 纳入3；_COPY_T_QUOTED_RE 有引号选项先例，-o 族无）
run("F-11-2 引号包输出选项", [
    ('curl "-o" CFG', "curl " + q2 + "-o" + q2 + " " + CFG + " http://x"),
    ("curl '-o' CFG", "curl " + q1 + "-o" + q1 + " " + CFG + " http://x"),
    ('curl "--output" CFG', "curl " + q2 + "--output" + q2 + " " + CFG + " http://x"),
    ('curl "-O" URL(红线负例)', "curl " + q2 + "-O" + q2 + " http://x/a.zip"),
])
# F-11-1：PS 冒号绑定形 -Destination:<值>（pwsh 活证可运行）
run("F-11-1 冒号绑定形", [
    ("Tee -FilePath:CFG", "Tee-Object -FilePath:" + CFG + " -InputObject x"),
    ("Copy -Destination:CFG 前置", "Copy-Item -Destination:" + CFG + " " + WS),
    ("Copy -Destination:引号CFG", "Copy-Item -Destination:" + q1 + CFG + q1 + " " + WS),
    ("Copy -Path:CFG Dest WS(源位应PASS)", "Copy-Item -Path:" + CFG + " -Destination " + WS),
])
# F-11-3：反向源位双标志第二标志形（round11-context §30 锁形精神：源位必PASS）
run("F-11-3 反向双标志", [
    ("Dest WS -LiteralPath CFG", "Copy-Item -Destination " + WS + " -LiteralPath " + CFG),
    ("Container x -Path CFG(Dest无值)", "Copy-Item -Container x -Path " + CFG + " -Destination " + WS),
    ("Dest WS 后置 Path CFG(活证PS写CFG=FP反例?)", "Copy-Item -Destination " + WS + " -Path " + CFG),
])
# F-11-2/4 邻域回潮锁：现状命中不得翻转
run("对照回潮锁(不得变化)", [
    ("独立 -o 现状", "curl -o " + CFG + " http://x"),
    ("粘连 -oCFG 现状", "curl -o" + CFG + " http://x"),
    ("-o= 现状", "curl -o=" + CFG + " http://x"),
])
