# PM round14 在途挖洞探针（只读 judge，round14 新支邻域 wave3）
import importlib.util, os
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
W = r"D:\myagent\workspace\write-guard"
spec = importlib.util.spec_from_file_location("p8", W + B + "handler.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
CFG = "D:" + B + "myagent" + B + ".hermes" + B + "config.yaml"
PDIR = "D:" + B + "myagent" + B + ".hermes" + B + "plugins" + B + "write-guard"
WS  = "D:" + B + "myagent" + B + "workspace"
Q = chr(34); SQ = chr(39)
def call(cmd):
    r = m.on_pre_tool_call("terminal", {"command": cmd}, "pm")
    return "PASS" if r is None else str(r.get("action"))

cases = [
    # of= 支门控：非 dd 命令带 of= 粘连（dd 门 _DD_RE.search(before) 把关）
    ("W3-1 cp \"of=<CFG>\" f  (非dd门, 期望 PASS 不误拦)", f'cp "of={CFG}" f.txt', "pass"),
    ("W3-2 dd \"of=<CFG>\" 双引号整包 (期望 hit)",            f'dd "of={CFG}" if=x bs=1', "hit"),
    ("W3-3 dd 'of=<CFG>' 单引号整包 (期望 hit)",              f"dd 'of={CFG}' if=x bs=1", "hit"),
    # 引号内前导空格（_pair_unquote 剥对后残留空格, of= 判定应失配=与端语义一致?）
    ("W3-4 dd \" of=<CFG>\" 引号内前导空格 (any 登记)",        f'dd " of={CFG}" if=x', "any"),
    # cluster 尾 o 大写 O 单字母: curl "-O" 大写红线(输出 URL 名非目标) vs "-o"
    ("W3-5 curl \"-O\" <CFG> 引号大写O (any: -O 语义=URL名, 保守弹可接受)", f'curl "-O" {CFG}', "any"),
    ("W3-6 curl \"-sO\" url 尾O大写cluster (any)",             'curl "-sO" http://x', "any"),
    # URL 整词含引号 o 尾词误命中面
    ("W3-7 grep foo \"baro\" file 引号词门外 (期望 PASS)",      f'grep foo "baro" file.txt', "pass"),
    # --target-directory 引号整包+等号内空格
    ("W3-8 cp \"--target-directory= <CFG>\" 空格形 (any)",      f'cp "--target-directory= {CFG}" f', "any"),
    # 载体内引号整包 dd of=
    ("W3-9 bash -c 内 dd \"of=<CFG>\" (期望 hit)",              "bash -c " + SQ + f'dd "of={CFG}" if=x' + SQ, "hit"),
    # install --target-directory 引号整包
    ("W3-10 install \"--target-directory=<PDIR>\" f (期望 hit)", f'install "--target-directory={PDIR}" f', "hit"),
    # robocopy -t? robocopy 用 /MOV 等, -t 族是否扩扰
    ("W3-11 robocopy 裸带 -t 非其语义 (any 登记)",               f'robocopy src dst -t{CFG}', "any"),
    # 误拦总锁: 引号整包 -t 非保护目录
    ("W3-12 cp \"-t<WS/dir>\" 非保护 (期望 PASS)",               f'cp "-t{WS}/dir" f', "pass"),
    # split/mv 带 -t? mv 无 -t 语义门控
    ("W3-13 mv \"-t<PDIR>\" f (mv 无-t语义, any 登记)",          f'mv "-t{PDIR}" f', "any"),
    # tee 单词 cmdlet 与 POSIX tee 混链
    ("W3-14 tee \"-a<CFG>\" cluster粘连POSIX (期望 hit)",        f'tee "-a{CFG}"', "any"),
]
nb = 0
for label, cmd, want in cases:
    got = call(cmd)
    okv = {"hit": got in ("approve", "block"), "pass": got == "PASS", "any": True}[want]
    nb += (not okv)
    print(f"{'ok ' if okv else 'FAIL'} {label:58s} -> {got}")
print(f"wave3 {len(cases)} 形: 符合预期 {len(cases)-nb}, 异常 {nb}")
