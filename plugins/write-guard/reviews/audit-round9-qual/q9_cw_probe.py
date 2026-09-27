# -*- coding: utf-8 -*-
"""round9 质量终审独立探针（只读，不改被测代码）：
A. _command_word 重写误拦面回归：≥18 例「新 vs 旧」提取对拍 + 端到端 act() 判定
B. S-5 载体裸形递归的额外误拦面
C. _GLUED_O_RE 名实逐条（注释声称 4 点）
D. _PS_WRITE_RE 词表名实（别名不扩声称）
E. _BARE_CARRIER_RE 与 _EMBED_SHELL_RE 互斥门名实
基线 HERMES_HOME / cwd 与 _verify_r9 同构造。"""
import importlib.util
import os
import re

B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
spec = importlib.util.spec_from_file_location(
    "wgq", "D:" + B + "myagent" + B + "workspace" + B + "write-guard" + B + "handler.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)

HOME = "D:/myagent/.hermes"
CFG = HOME + "/config.yaml"
HD = HOME + "/plugins/write-guard/handler.py"
GUARD = HOME + "/plugins/write-guard"
WS = "D:/myagent/workspace/a.txt"
SQ, DQ = chr(39), chr(34)
BAD, DIFF, OKN = [], [], 0


def act(tool, args):
    r = h.on_pre_tool_call(tool, args)
    return (r or {}).get("action") or "PASS"


# ---------- 旧实现复刻（git be14c7f 的 _command_word：仅取首 token） ----------
def old_cw(seg):
    m = h._SEG_HEAD_RE.match(seg)
    if not m:
        return None
    return m.group(1).strip("'\"").lower()


# ---------- A. _command_word 对拍（普通读/管道/cd 链/引号命令词/参数形态） ----------
CW_CASES = [
    # (输入 seg, 说明, 期望端到端方向)
    ("cat " + HD, "普通读：cat 守卫源码", "PASS"),
    ("ls -la D:/myagent/workspace", "选项后置读", "PASS"),
    ("findstr /c:\"a b\" D:/myagent/workspace/x.txt", "findstr /c:带值含空格", "PASS"),
    ("git -C D:/myagent/.hermes/plugins/write-guard status", "git -C 仓库定位（参数形）", "PASS"),
    ("git -c user.name=x commit -m y", "git -c 内联配置", "PASS"),
    ("grep -rn write-guard " + HOME, "grep -r 读守卫目录", "PASS"),
    ("tail -n 20 " + CFG, "tail -n 读配置", "PASS"),
    ("sed -n 1,10p " + CFG, "sed -n 只读打印", "PASS"),
    ("sort -o D:/myagent/workspace/out.txt d.txt", "sort -o 粘连非保护", "PASS"),
    ("head -c 100 " + HD, "head -c 读守卫", "PASS"),
    (DQ + "cp" + DQ + " evil D:/myagent/workspace/out", "引号命令词 cp（非保护目标）", "PASS"),
    (SQ + "echo" + SQ + " hi > " + WS, "引号命令词 echo 写 workspace", "PASS"),
    ("tar czf " + WS + " D:/myagent/workspace", "tar czf（非复制族，排除范围）", "PASS"),
    ("wc -l " + CFG, "wc 读配置", "PASS"),
    ("diff -u " + CFG + " " + CFG + ".bak", "diff 读（两参含配置）", "PASS"),
    ("tr -d x < " + HD, "tr 输入重定向读", "PASS"),
    ("cut -f1 -d: " + CFG, "cut -f/-d 带值选项读", "PASS"),
    ("chmod 644 " + WS, "chmod 非写语义族", "PASS"),
    ("rm -rf D:/myagent/workspace/tmp", "rm（平台层职责，插件不越权）", "PASS"),
    ("/bin/cat " + HD, "POSIX 绝对路径命令（以 / 开头 token）", "PASS"),
    ("/usr/local/bin/ls cp " + CFG, "绝对路径命令+后随 cp 词（剔除跳词风险）", "PASS"),
    ("cp -r " + HD + " D:/myagent/workspace/bk.py", "cp 源位=守卫文件（读侧）", "PASS"),
    ("echo hello | wc -c", "管道纯读", "PASS"),
    ("cat " + CFG + " | sort > " + WS, "管道读配置+写 workspace", "PASS"),
]
print("== A. _command_word 提取对拍（新 vs 旧） + 端到端 ==")
for seg, tag, want in CW_CASES:
    new = h._command_word(seg)
    old = old_cw(seg)
    got = act("terminal", {"command": seg})
    flag = ""
    if got != want:
        BAD.append("FP/方向: %s -> %s (期望 %s)" % (tag, got, want))
        flag = "  <<< 方向偏差"
    else:
        OKN += 1
    if new != old:
        DIFF.append((tag, old, new))
    print("  %-52s act=%-7s cw: %-22s -> %-22s%s" % (tag, got, str(old), str(new), flag))

print("\n-- 提取结果有差异的用例（=重写触及面清单）--")
for tag, old, new in DIFF:
    print("   %s: %r -> %r" % (tag, old, new))

# ---------- A2. 剔除链正确方向（本轮目标）：wrapper 前缀 + 复制族 ----------
print("\n== A2. wrapper 剔除的正向（应 approve/block，非 PASS） ==")
POS = [
    ("sudo cp evil " + GUARD, "approve", "sudo+cp 守卫目录"),
    ("runas /user:admin cp evil " + GUARD, "approve", "runas /user: 带值选项后 cp"),
    ("nohup cp evil " + GUARD, "approve", "nohup+cp"),
    ("LANG=C cp evil " + GUARD, "approve", "环境赋值+cp"),
    ("sudo truncate -s 0 " + CFG, "block", "sudo+truncate"),
    ("time cp evil " + GUARD, "approve", "time+cp"),
    ("env FOO=1 cp evil " + GUARD, "approve", "env+赋值+cp"),
    ("sudo -u root cp evil " + GUARD, "PASS", "登记边界：sudo 带值形（名义=放行）"),
]
for cmd, want, tag in POS:
    got = act("terminal", {"command": cmd})
    ok = got == want
    if not ok:
        BAD.append("正向: %s -> %s (期望 %s)" % (tag, got, want))
    OKN += bool(ok)
    print("  %-46s -> %-7s %s" % (tag, got, "ok" if ok else "FAIL"))

# ---------- B. S-5 额外误拦面 ----------
print("\n== B. S-5 载体裸形递归误拦面 ==")
S5 = [
    ("cmd /c dir " + HOME, "PASS", "cmd /c dir 守卫目录（纯列目录）"),
    ("cmd /c type " + HD, "PASS", "cmd /c type 读守卫源码"),
    ("cmd /c find " + CFG + " foo", "PASS", "cmd /c find 读配置"),
    ("sh -c 'echo hi'", "PASS", "sh -c 引号体无害"),
    ("bash -lc 'cd " + HOME + " && ls'", "PASS", "bash -lc 引号体 ls 守卫目录"),
    ("pwsh -NoProfile -Command Get-Process", "PASS", "pwsh -NoProfile 裸形读 cmdlet"),
    ("powershell.exe -Command Get-Content " + CFG, "block", "PS 读 cmdlet+受保护路径（既有矩阵口径）"),
    ("cmd /c copy " + HD + " D:/myagent/workspace/bk.py", "PASS", "守卫文件在源位（末位=workspace）"),
    ("bash -c 'curl -s http://x > /tmp/y'", "PASS", "递归内重定向非保护"),
]
for cmd, want, tag in S5:
    got = act("terminal", {"command": cmd})
    ok = got == want
    if not ok:
        BAD.append("S-5: %s -> %s (期望 %s)" % (tag, got, want))
    OKN += bool(ok)
    print("  %-50s -> %-7s %s" % (tag, got, "ok" if ok else "CHECK"))

# ---------- C. _GLUED_O_RE 注释声称逐条 ----------
print("\n== C. _GLUED_O_RE 名实对读 ==")
GR = h._GLUED_O_RE
claims = [
    ("^-[a-zA-Z]*[oO](?!=)(\\S+)$ 匹配 -oCFG", bool(GR.match("-o" + CFG))),
    ("匹配 cluster 前缀 -sSL-oHD 的 -oHD", bool(GR.match("-oHD"))),
    ("不匹配 -o=x（= 形排除，注释声称）", GR.match("-o=x" + CFG) is None),
    ("不匹配 -output=x 长形双 dash（注释声称双 dash 天然不匹）", GR.match("--output=" + CFG) is None),
    ("匹配 -O URL 尾（大写 O 亦收，注释含 -O）", bool(GR.match("-Ohttp://x/a.txt"))),
    ("不匹配裸 -o（无值，长度不足）", GR.match("-o") is None),
    ("不匹配 -L（不含 o/O）", GR.match("-L") is None),
]
for tag, res in claims:
    if not res:
        BAD.append("C 名实: " + tag)
    OKN += bool(res)
    print("  %-58s %s" % (tag, "符合" if res else "不符合"))

# 注释未言但行为存在的形态（找名实缺口）
EXTRA = ["-oL" + CFG, "-to" + CFG, "-O-o" + CFG, "-oo" + CFG, "-boO" + CFG, "-zot" + CFG]
print("  -- 额外粘连形态实测（cluster 含 o 且 o 非末位/多 o）--")
for t in EXTRA:
    print("     %-12s match=%s" % (t, bool(GR.match(t))))

print("\n== C2. 粘连门（_OUTPUT_FLAG_CMDS_RE=curl|wget|sort）名实 ==")
GATE = [
    ("curl -oCFG", "block"), ("wget -O" + CFG, "block"), ("sort -o" + CFG, "block"),
    ("grep -o" + CFG, "PASS"), ("tar -o" + CFG, "PASS"), ("tar -O" + CFG, "PASS"),
    ("dd -o" + CFG, "PASS"), ("python -o" + CFG, "PASS"),
]
for cmd, want in GATE:
    got = act("terminal", {"command": cmd})
    ok = got == want
    if not ok:
        BAD.append("C2 门: %s -> %s (期望 %s)" % (cmd, got, want))
    OKN += bool(ok)
    print("  %-34s -> %-7s %s" % (cmd[:34], got, "ok" if ok else "FAIL"))

# ---------- D. _PS_WRITE_RE 名实 ----------
print("\n== D. _PS_WRITE_RE 扩集名实 ==")
PW = h._PS_WRITE_RE
for w, want in [("Copy-Item", True), ("Tee-Object", True), ("cp", False), ("tee", False),
                ("Set-Content", True), ("Out-File", True), ("Add-Content", True),
                ("Get-Content", False), ("CopyItem", True), ("Copy-To", True)]:
    got = PW.search(w + " x") is not None
    note = ""
    if got != want:
        BAD.append("D 词表: %s -> %s (声称 %s)" % (w, got, want))
    if w.startswith("Copy") and got and w not in ("Copy-Item",):
        note = "  (\\b 对连字符词的内部边界效应，见报告)"
    OKN += 1
    print("  %-14s in_set=%-5s 声称=%-5s%s" % (w, got, want, note))
print("  词元完整性:", [m for m in re.findall(r"[A-Za-z-]+", PW.pattern) if m not in ("b", "i", "i", "IGNORECASE")][:20])

# ---------- E. 互斥门与深度门 ----------
print("\n== E. _BARE_CARRIER_RE / _EMBED_SHELL_RE 互斥 + 深度门 ==")
print("  BARE 匹配 cmd /c copy …:", bool(h._BARE_CARRIER_RE.match("cmd /c copy evil " + CFG)))
print("  EMBED 匹配同段（应 False）:", bool(h._EMBED_SHELL_RE.search("cmd /c copy evil " + CFG)))
q = 'cmd /c "copy evil ' + CFG + '"'
print("  引号体 EMBED=True:", bool(h._EMBED_SHELL_RE.search(q)), " BARE=True:", bool(h._BARE_CARRIER_RE.match(q)))
print("  BARE 载体词集:", re.findall(r"pwsh|powershell|cmd|bash|sh|zsh|ksh|dash", h._BARE_CARRIER_RE.pattern)[:12])
print("  注释声称载体集含 [A-Za-z] 开关位形 \\w*（实测）:", h._BARE_CARRIER_RE.match("sh --x -c cp evil " + CFG) is not None)
print("  深度门常量:", h._NEST_DEPTH_LIMIT)
print("  四层载体套壳 cmd /c cmd /c cmd /c cmd /c copy CFG:",
      act("terminal", {"command": "cmd /c cmd /c cmd /c cmd /c copy evil " + CFG}))
print("  三层 cmd /c cmd /c cmd /c copy evil CFG:",
      act("terminal", {"command": "cmd /c cmd /c cmd /c copy evil " + CFG}))

# ---------- F. S-3 单& 残余 FP 面独立扩测 ----------
print("\n== F. S-3 单 & 独立扩测（声称引号感知不误切） ==")
AMP = [
    ('curl "https://x/y?a=1&b=2" > ' + WS, "PASS", "双引号 URL & + 重定向 ws"),
    ("curl 'https://x?a=1&b=2'", "PASS", "单引号 URL &"),
    ('curl -G -d "a=1&b=2" http://x > ' + WS, "PASS", "-d 引号 & 写 ws"),
    ("echo a && b & echo c", "PASS", "混合 && & 无保护词"),
    ("copy a " + WS + " & copy b " + WS, "PASS", "cmd & 链双非保护"),
    ("echo x>&2 & echo y", "PASS", "> & 粘连（>&2 残段）"),
    ("start /b a.exe & b.exe " + CFG, "PASS", "& 后段路径为末位但非写语义"),
    ("findstr a&b " + WS, "PASS", "裸 a&b 分段后无保护词"),
    ("reg query HKLM /f a&b", "PASS", "reg & 形"),
    ("echo x 2>&1 && cp evil " + GUARD, "approve", "&& 与 2>&1 混用仍命中（不新漏）"),
    ("echo x & cp evil " + GUARD, "approve", "单 & 命中（本轮目标）"),
    ("echo x & echo y > " + CFG, "block", "残段 > CFG 独立识别（声称成立）"),
]
for cmd, want, tag in AMP:
    got = act("terminal", {"command": cmd})
    ok = got == want
    if not ok:
        BAD.append("F: %s -> %s (期望 %s)" % (tag, got, want))
    OKN += bool(ok)
    print("  %-44s -> %-7s %s" % (tag, got, "ok" if ok else "FAIL"))

print("\n总计 ok=%d，偏差 %d 条" % (OKN, len(BAD)))
for x in BAD:
    print("  [X] " + x)
