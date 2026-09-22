# round12 安全路探针 A：F-11-1~4 修复复测·双向差分（封堵向+误拦向，PM 指定邻域重点）
# 对照代际：new=4e254c8(现行) / r11=94998f5(上一轮) / r10=2cc28cf。
# 期望值一律以 boundary 语义 + pwsh/curl 可运行性独立推导，非照抄 fix-012 §0（独立复测）。
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
r11 = load("h11", os.path.join(HERE, "..", "..", "_r2tmp", "handler_r11_94998f5.py"))
r10 = load("h10", os.path.join(HERE, "..", "audit-round10-qual", "base", "handler_r10commit.py"))

HOME = "D:/myagent/.hermes"
CFG = HOME + "/config.yaml"
GSRC = HOME + "/plugins/write-guard/handler.py"
WS = "D:/myagent/workspace/a.txt"
BAK = "D:/myagent/workspace/bak.yaml"
URL = "http://x/y.tar.gz"

def act(mod, cmd):
    r = mod.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action") or "PASS"

fails = 0
def run(group, cases):
    global fails
    print("---", group, "---")
    for tag, cmd, want in cases:
        got = act(new, cmd)
        o11, o10 = act(r11, cmd), act(r10, cmd)
        mark = "ok  " if got == want else "DIFF"
        if got != want: fails += 1
        print(f"[{mark}] new={got:8s} want={want:8s} | r11={o11:8s} r10={o10:8s} | {tag} :: {cmd!r}")

# ================= F-11-1 冒号粘连（改动2）=================
run("F11-1 攻击向", [
    ("a1 Dest:CFG", "Copy-Item -Destination:" + CFG + " " + WS, "approve"),
    ("a2 FP:CFG Tee", "Tee-Object -FilePath:" + CFG + " -InputObject x", "approve"),
    ("a3 Dest:'CFG' 单引值", "Copy-Item -Destination:" + q1 + CFG + q1 + " " + WS, "approve"),
    ("a3b Dest:\"CFG\" 双引值", "Copy-Item -Destination:" + q2 + CFG + q2 + " " + WS, "approve"),
    ("a5 Dest:GSRC 守卫源码(复制族=弹卡向,处置分流)", "Copy-Item -Destination:" + GSRC + " " + WS, "approve"),
    ("a6 混排大小写 -dEsTiNaTiOn:", "Copy-Item -dEsTiNaTiOn:" + CFG + " " + WS, "approve"),
    ("a7 链式×载体内嵌", 'pwsh -Command "Copy-Item -Destination:' + CFG + ' x"', "approve"),
    ("a8 冒号形目标非保护值", "Copy-Item -Destination:D:/ws/x.txt " + CFG, "PASS"),
])
run("F11-1 边界/误拦向", [
    ("a4 等号形(PM活证PS拒绝=附录)", "Copy-Item -Destination=" + CFG + " " + WS, "PASS"),
    ("a9 引号包选项词(PM活证PS拒绝)", "Copy-Item '-Destination' " + CFG + " " + WS, "PASS"),
    ("a10 值含 dash -Dest:\"-x\"", "Copy-Item -Destination:" + q2 + "-x" + q2 + " " + CFG, "PASS"),
    ("a10b 值含 dash 裸形 -Dest:-x", "Copy-Item -Destination:-x " + CFG, "PASS"),
    ("a11 后随标志否决保持(双标志B族)", "Copy-Item -Destination:" + CFG + " -Container " + BAK, "PASS"),
    ("a12 冒号形×反向源位", "Copy-Item -Path:" + CFG + " -Destination " + BAK, "PASS"),
])
# ================= F-11-2 引号选项词（改动3）=================
run("F11-2 攻击向", [
    ("b1 curl \"-o\" CFG", 'curl "-o" ' + CFG + " " + URL, "block"),
    ("b2 curl '-o' CFG", "curl '-o' " + CFG + " " + URL, "block"),
    ("b3 curl \"--output\" CFG", 'curl "--output" ' + CFG + " " + URL, "block"),
    ("b3b curl \"--output-document\"", 'curl "--output-document" ' + CFG + " " + URL, "block"),
    ("b10 wget \"-O\" CFG(大写语义向)", 'wget "-O" ' + CFG + " " + URL, "block"),
])
run("F11-2 误拦向", [
    ("b4 grep \"-o\" 门外", 'grep "-o" ' + CFG, "PASS"),
    ("b5 curl \"-O\" URL 红线向", 'curl "-O" ' + URL, "PASS"),
    ("b6 curl \"-o\" 非保护", 'curl "-o" D:/ws/x.txt ' + URL, "PASS"),
    ("b7 任意引号token不误命中", 'curl "header: X" ' + CFG, "PASS"),
    ("b8 引号交叉值 \"-o<x>\"(排除1穿插)", 'curl "-o' + CFG + '" ' + URL, "PASS"),
    ("b9 sort \"-o\" CFG(门内)", 'sort "-o" ' + CFG + " d.txt", "block"),
])
# ================= F-11-3 收窄+三向锁（改动1）=================
run("F11-3 归正向", [
    ("c1 Dest WS -Path CFG", "Copy-Item -Destination " + WS + " -Path " + CFG, "PASS"),
    ("c2 Dest WS -LiteralPath CFG", "Copy-Item -Destination " + WS + " -LiteralPath " + CFG, "PASS"),
    ("c5 单标志 -Path CFG 末位非保护", "Copy-Item -Path " + CFG + " " + BAK, "PASS"),
])
run("F11-3 三向锁形零回退", [
    ("c4 前置封堵 -Destination CFG 非保护", "Copy-Item -Destination " + CFG + " " + WS, "approve"),
    ("c6 Tee -FilePath CFG", "Tee-Object -FilePath " + CFG + " -InputObject x", "approve"),
    ("c3 反向锁 -Path CFG -Destination WS", "Copy-Item -Path " + CFG + " -Destination " + WS, "PASS"),
    ("B 双标志 -Container CFG -Destination 非保护", "Copy-Item -Container " + CFG + " -Destination " + WS, "PASS"),
    ("B2 双标志 -Path CFG -Destination BAK", "Copy-Item -Path " + CFG + " -Destination " + BAK, "PASS"),
    ("源位读红线 Copy-Item CFG BAK", "Copy-Item " + CFG + " " + BAK, "PASS"),
    ("前置守卫源码(复制族处置=弹卡)", "Copy-Item -Destination " + GSRC + " " + WS, "approve"),
])
run("F11-3/Q-11-1 邻域(锁形1 前置+位参目标·PM活证真写)", [
    ("n1 前置 -Path CFG -Dest BAK", "Copy-Item -Path " + CFG + " -Destination " + BAK + " x", "PASS"),
    ("n2 -LiteralPath CFG 位参目标", "Copy-Item -LiteralPath " + CFG + " " + BAK, "PASS"),
    ("n3 引号值整词 -Destination \"CFG\"", 'Copy-Item -Destination "' + CFG + '" ' + WS, "approve"),
    ("n4 TAB 分隔前置", "Copy-Item\t-Destination\t" + CFG + "\t" + WS, "approve"),
])
# ================= F-11-4 cluster 尾o（改动4）=================
run("F11-4 攻击向", [
    ("d1 curl -so CFG", "curl -so " + CFG + " " + URL, "block"),
    ("d2 curl -sSLfo CFG", "curl -sSLfo " + CFG + " " + URL, "block"),
    ("d3 wget -qO CFG", "wget -qO " + CFG + " " + URL, "block"),
    ("d4 sort -ro CFG", "sort -ro " + CFG + " d.txt", "block"),
    ("d5 双dash cluster -Xo?", "curl --output " + CFG + " " + URL, "block"),
])
run("F11-4 误拦向(PM 指定邻域)", [
    ("d6 curl -so 非保护", "curl -so D:/ws/x.txt " + URL, "PASS"),
    ("d7 --http1.0 数字尾", "curl --http1.0 " + CFG, "PASS"),
    ("d8 --http1.0 带值", "curl --http1.0 -v " + CFG, "PASS"),
    ("d9 curl -O CFG(登记保守族,r11同block)", "curl -O " + CFG, "block"),
    ("d9b curl -sSO CFG 大写尾o cluster(与-O同族保守,r12并支一致)", "curl -sSO " + CFG, "block"),
    ("d10 curl -z ts -O URL", 'curl -z ts -O "' + URL + '"', "PASS"),
    ("d11 grep -o 门外", "grep -o " + CFG, "PASS"),
    ("d12 mount -o 门内词不含", "mount -o remount " + CFG, "PASS"),
    ("d13 sort ws/o 归正不回潮", "sort d.txt ws/o", "PASS"),
    ("d14 URL 尾 /o 不回潮", "curl " + HOME + "/x/o", "PASS"),
    ("d15 URL 尾 -o 不回潮", "curl http://x/pro-o", "PASS"),
    ("d16 curl -sfo=CFG(curl活证写名含=,非等价形→附录)", "curl -sfo=" + CFG + " " + URL, "PASS"),
    ("d17 未知命令 -so", "mytool -so " + CFG, "PASS"),
    ("d18 my-dir-o 附录⑥不回潮", "sort d.txt D:/ws/my-dir-o", "PASS"),
])
# ================= F-10-1/F-10-2 不回潮 + 红线四形 =================
run("不回潮锁", [
    ("裸 -o block", "curl -o " + CFG + " " + URL, "block"),
    ("-o= 等号 block", "curl -o=" + CFG + " " + URL, "block"),
    ("-o粘连 block", "curl -o" + CFG + " " + URL, "block"),
    ("/O cmd 方言 block", "sort /O" + CFG + " d.txt", "block"),
    ("Set-Content 出现即写", "Set-Content -Path " + CFG + " -Value x", "block"),
    ("cp 直写配置弹卡", "cp x " + CFG, "approve"),
    ("cp 守卫源码(复制族处置=弹卡,B3分流)", "cp evil.py " + GSRC, "approve"),
    ("rm -r home 分层不扩", "rm -rf D:/myagent/.hermes", "PASS"),
    ("gateway restart block", "hermes gateway restart", "block"),
    ("gateway status 不误伤", "hermes gateway status", "PASS"),
    ("bash -c 内嵌一层", 'bash -c "curl -so ' + CFG + ' ' + URL + '"', "block"),
])
print("PROBE-A FAILS:", fails)
