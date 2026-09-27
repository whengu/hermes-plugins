# round11 安全路探针 B：纳入范围新旁路搜寻（F-10-1/F-10-2 修复邻域组合面）+ 误拦向搜寻
import importlib.util, os
BS, q1, q2 = chr(92), chr(39), chr(34)
os.environ["HERMES_HOME"] = "D:" + BS + "myagent" + BS + ".hermes"
os.chdir("D:" + BS + "myagent" + BS + "workspace")
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("hn", os.path.join(HERE, "..", "..", "handler.py"))
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
r10spec = importlib.util.spec_from_file_location("hr10", os.path.join(HERE, "..", "audit-round10-qual", "base", "handler_r10commit.py"))
r10 = importlib.util.module_from_spec(r10spec); r10spec.loader.exec_module(r10)

HOME = "D:/myagent/.hermes"
CFG = HOME + "/config.yaml"
WS = "D:/myagent/workspace/a.txt"
BAK = "D:/myagent/workspace/bak.yaml"
GUARD = HOME + "/plugins/write-guard"
BT = chr(96)

def act(mod, cmd):
    r = mod.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action") or "PASS"

def run(group, cases):
    print("---", group, "---")
    for tag, cmd, want in cases:
        got, o = act(h, cmd), act(r10, cmd)
        mark = "ok  " if (got == want or want == "?") else "DIFF"
        print(f"[{mark}] new={got:8s} want={want:8s} r10={o:8s} | {tag} :: {cmd!r}")

# 误拦向：真实 PS 语义 CFG=源，若命中即 FP（纳入范围误拦候选）
run("B1 误拦向·PS 语义源位混合形", [
    ("Path CFG Dest BAK(源位,无末位CFG)", "Copy-Item -Path " + CFG + " -Destination " + BAK, "PASS"),
    ("Path CFG 后置 Dest WS 链", "Copy-Item -Destination " + WS + " -Path " + CFG, "?"),
    ("多源 Dest CFG 末位(写向)", "Copy-Item -Path " + WS + " " + BAK + " -Destination " + CFG, "approve"),
    ("Dest 数组双值含CFG(保守向可接受)", "Copy-Item -Destination " + CFG + " " + WS + " " + BAK, "?"),
])
# 旁路向：常规可运行攻击形（纳入范围新旁路候选）
run("B2 攻击向·载体/链式组合新面", [
    ("&&链 反向源位(必PASS)", "Copy-Item -Destination " + WS + " " + CFG + " && echo done", "PASS"),
    (";链 前置命中", "notepad; Copy-Item -Destination " + CFG + " " + WS, "approve"),
    ("bash -c 内 pwsh 前置(两嵌套=排除4)", 'bash -c "pwsh -Command \'Copy-Item -Destination "D:/myagent/.hermes/config.yaml"\'"', "?"),
    ("pwsh 单引号体前置", "pwsh -Command 'Copy-Item -Destination " + CFG + " " + WS + "'", "approve"),
    ("sudo bash -c 内嵌 Copy-Item 前置", 'sudo bash -c "pwsh -Command \\"Copy-Item -Destination ' + CFG + " " + WS + '\\""', "?"),
    ("-Destination 大小写混", "Copy-Item -dEsTiNaTiOn " + CFG + " " + WS, "approve"),
    ("-Destination: 冒号形(PS 合法)", "Copy-Item -Destination:" + CFG + " " + WS, "?"),
    ("-Destination= 等号形(PS5+ 合法?)", "Copy-Item -Destination=" + CFG + " " + WS, "?"),
    ("裸 Dest 缩写前置(冷知识对照)", "Copy-Item -Dest " + CFG + " " + WS, "?"),
    ("Tee -Append+FilePath 前置", "Tee-Object -FilePath " + CFG + " -Append -InputObject x", "approve"),
    ("Set-Content 别名 sc CFG 位参(别名登记)", "sc " + CFG + " x", "?"),
    ("载体大小写 PWSH", 'PWSH -c "Copy-Item -Destination ' + CFG + " " + WS + '"', "?"),
])
# PS 续行形（backtick+LF——纳入2 只列 bs+LF；实测登记）
run("B3 续形·backtick 续行 / bs 换行(纳入2 面)", [
    ("PS backtick 续行前置", "Copy-Item -Destination " + BT + "\n" + CFG + " " + WS, "?"),
    ("shell bs+LF 前置(纳入2)", "Copy-Item -Destination \\\n" + CFG + " " + WS, "approve"),
    ("CRLF 续行前置", "Copy-Item -Destination \\\r\n" + CFG + " " + WS, "approve"),
    ("裸换行分链前置", "echo x\nCopy-Item -Destination " + CFG + " " + WS, "approve"),
    ("NL 形 -o(纳入2 \\n)", "printf 'x'\\ncurl -o\\n" + CFG + "\\nhttp://x", "block"),
])
# F-10-2 残余邻域：真输出标志但在非常规位置/带引号
run("B4 F-10-2 邻域", [
    ("curl 前置-o后URL", "curl -o " + CFG, "block"),
    ("sort CFG 后置-o(源位?)", "sort " + CFG + " -o out.txt", "?"),
    ("引号包 -o 选项", 'curl "-o" ' + CFG + " http://x", "block"),
    ("引号包 --output", 'curl "--output" ' + CFG + " http://x", "block"),
    ("URL 含 query 尾 o", "curl 'http://x?q=o' " + CFG, "PASS"),
    ("sort -o=out 等号短形", "sort -o=" + CFG + " d.txt", "block"),
    ("cluster -sfo 末 o 粘连", "curl -sfo" + CFG + " http://x", "block"),
    ("wget -O- 管道丢弃", "wget -O- http://x > " + WS, "block"),
    ("curl -O 两 URL 负例", "curl -O http://x/a http://x/b", "PASS"),
    ("sort /o 小写独立", "sort /o " + CFG + " d.txt", "block"),
])
