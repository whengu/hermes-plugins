# round11 安全路探针 A：F-10-1/F-10-2 修复复测（每族攻击形+误拦负例，r9/r10/r11 三代对照）
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
r10 = load("hr10", os.path.join(HERE, "..", "audit-round10-qual", "base", "handler_r10commit.py"))
r9 = load("hr9", os.path.join(HERE, "..", "audit-round10-sec", "handler_r9_cbd6301.py"))

HOME = "D:/myagent/.hermes"
CFG = HOME + "/config.yaml"
WS = "D:/myagent/workspace/a.txt"
BAK = "D:/myagent/workspace/bak.yaml"
GUARD = HOME + "/plugins/write-guard"

def act(mod, cmd):
    r = mod.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action") or "PASS"

def run(group, cases):
    print("---", group, "---")
    for tag, cmd, want in cases:
        got = act(new, cmd)
        o10, o9 = act(r10, cmd), act(r9, cmd)
        mark = "ok  " if got == want else "DIFF"
        print(f"[{mark}] new={got:8s} want={want:8s} | r10={o10:8s} r9={o9:8s} | {tag} :: {cmd!r}")

# ========== F-10-1 三锁形（round11-context §30 指定必测）==========
run("F10-1 锁形1 前置命中", [
    ("前置 -Destination CFG", "Copy-Item -Destination " + CFG + " " + WS, "approve"),
    ("前置 -FilePath Tee", "Tee-Object -FilePath " + CFG + " -InputObject x", "approve"),
    ("前置 -Path CFG(Copy-Item)", "Copy-Item -Path " + CFG + " -Destination " + BAK + " -x", "approve"),  # 意图: -Path即目标? 实为源位形——见锁形3
])
run("F10-1 锁形2 反向源位 PASS", [
    ("反向 Dest WS CFG(源)", "Copy-Item -Destination " + WS + " " + CFG, "PASS"),
    ("反向×载体", 'pwsh -Command "Copy-Item -Destination ' + WS + " " + CFG + '"', "PASS"),
    ("Tee 源位在标志前 <CFG> -FilePath WS", "Tee-Object " + CFG + " -FilePath " + WS, "PASS"),
    ("Copy 位参前置 <CFG> 非保护 -Destination WS", "Copy-Item " + CFG + " " + BAK + " -Destination " + WS, "PASS"),
])
run("F10-1 锁形3 双标志 PASS", [
    ("双标志 Container CFG Dest BAK", "Copy-Item -Container " + CFG + " -Destination " + BAK, "PASS"),
    ("双标志 Path CFG Dest BAK", "Copy-Item -Path " + CFG + " -Destination " + BAK, "PASS"),
    ("双标志 LiteralPath CFG Dest BAK", "Copy-Item -LiteralPath " + CFG + " -Destination " + BAK, "PASS"),
])
# ========== F-10-1 其余族攻击形 ==========
run("F10-1 封堵向变体", [
    ("尾位锁 n", "Copy-Item evil.txt -Destination " + CFG, "approve"),
    ("前置守卫目录", "Copy-Item -Destination " + GUARD + " " + WS, "approve"),
    ("小写混排", "COPY-item -DESTINATION " + CFG + " " + WS, "approve"),
    ("制表符分隔", "Copy-Item\t-Destination\t" + CFG + "\t" + WS, "approve"),
    ("&&链式前置", "echo hi && Copy-Item -Destination " + CFG + " " + WS, "approve"),
    ("管道前置", "echo x | Copy-Item -Destination " + CFG + " " + WS, "approve"),
    ("sudo pwsh 载体", 'sudo pwsh -Command "Copy-Item -Destination ' + CFG + " " + WS + '"', "approve"),
    ("引号值整词", "Copy-Item -Destination " + q1 + CFG + q1 + " " + WS, "approve"),
    ("双引号值整词", "Copy-Item -Destination " + q2 + CFG + q2 + " " + WS, "approve"),
    ("cmd 载体 Copy-Item", 'cmd /c "Copy-Item -Destination ' + CFG + " " + WS + '"', "approve"),
])
# ========== F-10-1 缩写别名面（PS 唯一前缀缩写惯例）==========
run("F10-1 缩写别名形", [
    ("-Dest 前置", "Copy-Item -Dest " + CFG + " " + WS, "?"),
    ("-Dest 尾位(末位启发)", "Copy-Item evil -Dest " + CFG, "approve"),
    ("-PsPath 前置(Path 唯一别名)", "Copy-Item -PsPath " + CFG + " -Destination " + BAK, "?"),
    ("-OutFile 前置(Set-Content 别名 OutFile)", "Set-Content -OutFile " + CFG + " -Value x", "block"),
])
# ========== F-10-1 回潮负例 ==========
run("F10-1 不回潮负例", [
    ("Set-Content 裸形 block", "Set-Content " + CFG + " x", "block"),
    ("Set-Content -Path block", "Set-Content -Path " + CFG + " -Value x", "block"),
    ("Add-Content block", "Add-Content " + CFG + " x", "block"),
    ("Out-File 尾位 block", "echo x | Out-File " + CFG, "block"),
    ("cp 源位零差", "cp " + CFG + " " + BAK, "PASS"),
    ("cp 目标零差", "cp " + BAK + " " + CFG, "approve"),
    ("rsync 源位零差", "rsync -av " + CFG + " " + WS, "PASS"),
    ("Get-Content 读", "Get-Content -Path " + CFG, "PASS"),
    ("引号标志不可运行形锁现状", "Copy-Item " + q1 + "-Destination" + q1 + " " + CFG + " " + WS, "PASS"),
])
# ========== F-10-2 真·输出标志形保持（本轮任务指定四形）==========
run("F10-2 真输出标志保持", [
    ("-o 独立", "curl -o " + CFG + " http://x", "block"),
    ("-o 独立(空格等号)", "curl -o = " + CFG + " http://x", "block"),
    ("-o 粘连", "curl -o" + CFG + " http://x", "block"),
    ("cluster -sSL -o 独立", "curl -sSL -o " + CFG + " http://x", "block"),
    ("cluster+粘连 -sSL -oCFG", "curl -sSL -o" + CFG + " http://x", "block"),
    ("cluster 内含 o -Oz 形(非 o 收尾)", "curl -z ts -O " + q2 + "http://x/a.zip" + q2, "PASS"),
    ("-O 大写独立 URL 红线", "curl -O http://x/a.zip", "PASS"),
    ("-O 独立 + 受保护 URL 位", "curl -O " + CFG, "?"),
    ("/O 独立 sort F-9-3 锁", "sort /O " + CFG + " d.txt", "block"),
    ("/O 粘连 sort", "sort /O" + CFG + " d.txt", "block"),
    ("--output 长形", "curl --output " + CFG + " http://x", "block"),
    ("--output= 等号", "curl --output=" + CFG + " http://x", "block"),
    ("--output-document", "wget --output-document " + CFG + " http://x", "block"),
    ("-o=/等号粘连", "curl -o=" + CFG + " http://x", "block"),
    ("wget -O 独立", "wget -O " + CFG + " http://x", "block"),
    ("sort -o 不回潮", "sort -o " + CFG + " d.txt", "block"),
    ("CURL 大写", "CURL -O" + CFG + " http://x", "block"),
])
# ========== F-10-2 误拦归正保持 ==========
run("F10-2 归正向", [
    ("sort ws/o CFG", "sort " + "D:/myagent/workspace/o" + " " + CFG, "PASS"),
    ("sort ws/O CFG", "sort D:/myagent/workspace/O " + CFG, "PASS"),
    ("curl URL /o CFG", "curl http://x/o " + CFG, "PASS"),
    ("wget URL /o CFG", "wget http://x/f/o " + CFG, "PASS"),
    ("附录⑥ my-dir-o", "sort D:/myagent/workspace/my-dir-o " + CFG, "PASS"),
    ("home 内目录 o 形", "sort " + HOME + "/o " + CFG, "PASS"),
    ("段首 -o 未知命令放行", "tool -o " + CFG, "?"),
    ("grep -o 负例", "grep -o pat " + CFG, "PASS"),
]  )
