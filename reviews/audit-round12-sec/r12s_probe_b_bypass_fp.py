# round12 安全路探针 B：纳入范围新旁路搜寻（本轮改动邻域）+ PM 转来 X-13 候选独立复核
# 含 pwsh 活证（_r2tmp/r12s 草样，零受保护路径触碰）。三代对照 new/r11/r10。
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

def run(group, cases):
    print("---", group, "---")
    for tag, cmd, want in cases:
        got = act(new, cmd)
        o11, o10 = act(r11, cmd), act(r10, cmd)
        mark = "ok  " if got == want else "DIFF"
        print(f"[{mark}] new={got:8s} want={want:8s} | r11={o11:8s} r10={o10:8s} | {tag} :: {cmd!r}")

# ===== 候选 1：cluster 尾 o + 等号粘连（curl 8.1.2 活证：写入文件名字面含 = 前缀
# （live 产物 =live_laplace.bin），短选项族 `=` 不解析为分隔符 → 非可运行同义形，
# 期望改 PASS 附录；裸 -o= 的既有 block 系 r10 保守锁，不据 cluster 差立旁路项） =====
run("cluster尾o×等号粘连(活证非等价形)", [
    ("curl -sfo=CFG", "curl -sfo=" + CFG + " " + URL, "PASS"),
    ("curl -so=CFG", "curl -so=" + CFG + " " + URL, "PASS"),
    ("wget -qO=CFG", "wget -qO=" + CFG + " " + URL, "PASS"),
    ("sort -ro=CFG", "sort -ro=" + CFG + " d.txt", "PASS"),
    ("NEG -so=非保护", "curl -so=D:/ws/x.txt " + URL, "PASS"),
    ("NEG --url=尾o长词(门外值)", "curl --url=" + WS + " " + URL, "PASS"),
    ("NEG 数字尾= --http1.0=1", "curl --http1.0=1 " + CFG, "PASS"),
    ("NEG sort -o= 回归", "curl -o=" + CFG + " " + URL, "block"),
])
# ===== 候选 2/3：PM X-13-1 真目标先绑+源参标志后随 =====
run("X-13-1 命名支后置否决过宽", [
    ("X1 Dest CFG -Path WS", "Copy-Item -Destination " + CFG + " -Path " + WS, "approve"),
    ("X2 Dest CFG -LiteralPath WS", "Copy-Item -Destination " + CFG + " -LiteralPath " + WS, "approve"),
    ("X3 Dest:CFG -Path WS 冒号形", "Copy-Item -Destination:" + CFG + " -Path " + WS, "approve"),
    ("X3b Dest:CFG -LiteralPath GSRC", "Copy-Item -Destination:" + CFG + " -LiteralPath " + BAK, "approve"),
    ("X5 Dest CFG -Recurse(非ANY)", "Copy-Item -Destination " + CFG + " -Recurse", "approve"),
    ("X6 Dest CFG -ToDouble -Path WS", "Copy-Item -Destination " + CFG + " -ToDouble -Path " + WS, "PASS"),
    ("X7 Dest GSRC -Path WS(守卫源)", "Copy-Item -Destination " + GSRC + " -Path " + WS, "approve"),
])
# ===== 候选：Tee per-cmd 语义 =====
run("X-13-2 Tee 目标词表", [
    ("T1 Tee -LiteralPath CFG 末位", "Tee-Object -LiteralPath " + CFG, "approve"),
    ("T2 Tee -LiteralPath CFG 前置", "Tee-Object -LiteralPath " + CFG + " -InputObject x", "approve"),
    ("T2b Tee LP CFG -FilePath WS(真目标竞绑)", "Tee-Object -LiteralPath " + CFG + " -FilePath " + WS, "PASS"),
    ("T4 Tee -FilePath CFG(保持)", "Tee-Object -FilePath " + CFG + " -InputObject x", "approve"),
    ("T5 Tee -Encoding x CFG(位参末)", "Tee-Object -Encoding utf8 " + CFG, "approve"),
])
# ===== 命名支引号交叉/粘连组合面 =====
run("引号×粘连交叉", [
    ("整词引号目标值 Dest \"CFG\"", "Copy-Item -Destination " + q2 + CFG + q2 + " " + WS, "approve"),
    ("整词引号目标值 Dest 'CFG'", "Copy-Item -Destination " + q1 + CFG + q1 + " " + WS, "approve"),
    ("冒号粘连引号值×后随源参", "Copy-Item -Destination:" + q2 + CFG + q2 + " -Path " + WS, "approve"),
    ("引号包整词粘连 \"-Destination:CFG\"", "Copy-Item " + q2 + "-Destination:" + CFG + q2 + " " + WS, "PASS"),
    ("引号包整词粘连+尾随值 \"-Destination:CFG\" WS(引号剥后同义·pwsh待活证)", "Copy-Item " + q2 + "-Destination:" + CFG + q2 + " " + WS, "PASS"),
    ("单引号包冒号整词+尾随值 '-Dest:CFG' WS", "Copy-Item '-Destination:" + CFG + "' " + WS, "PASS"),
    ("curl \"-o\"=CFG 引号×等号交叉", "curl " + q2 + "-o" + q2 + "=" + CFG + " " + URL, "PASS"),
    ("单引号包选项+冒号值 '-Destination:CFG'", "Copy-Item '-Destination:" + CFG + "' " + WS, "PASS"),
    ("Dest:\"\" 空值交叉", "Copy-Item -Destination:" + q2 + q2 + " " + CFG, "PASS"),
])
# ===== curl/wget/sort 组合面：多旗标+o 中位 =====
run("cluster 中位o/组合旗标", [
    ("curl -fo CFG(-f静默+-o)", "curl -fo " + CFG + " " + URL, "block"),
    ("curl -sS -o CFG", "curl -sS -o " + CFG + " " + URL, "block"),
    ("curl -s -o CFG -v", "curl -s -o " + CFG + " -v " + URL, "block"),
    ("curl -o CFG 前置多值", "curl -H x:y -o " + CFG + " " + URL, "block"),
    ("NEG curl -O -s CFG 分离大写", "curl -O -s " + CFG, "block"),
    ("NEG curl -sSO URL 大写下载名", "curl -sSO " + URL, "PASS"),
    ("NEG wget --output-document CFG", "wget --output-document " + CFG + " " + URL, "block"),
])
# ===== 误拦邻域：值含 dash、cluster 邻词 =====
run("误拦邻域", [
    ("NEG curl -o -x CFG(带值参干扰)", "curl -o " + WS + " -x proxy " + URL, "PASS"),
    ("NEG sort -o 非保护", "sort -o D:/ws/x.txt d.txt", "PASS"),
    ("NEG curl 尾o长词 --write-out CFG", "curl --write-out %{http_code} " + CFG, "PASS"),
    ("NEG --http1.0 cluster 邻", "curl --http1.0 --compressed " + CFG, "PASS"),
    ("NEG -o 在引号体中间不成词", "curl x \"-o\" " + WS + " " + URL, "PASS"),
    ("NEG echo 文本含 -so 与路径", "echo curl -so " + CFG, "PASS"),
])
# ===== X-13 复核定级：r11 同形对照（是否 round12 新引入） =====
run("回潮判定对照(r11应同值)", [
    ("X1 同形", "Copy-Item -Destination " + CFG + " -Path " + WS, "approve"),
    ("T1 同形(r11=approve 若成立则非新引入)", "Tee-Object -LiteralPath " + CFG, "approve"),
])
