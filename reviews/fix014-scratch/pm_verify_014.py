# round14 验收断言（F-13-S1/X-14-1 合并洞修复靶心 + 锁形）
# 基线 round13 10a2094 预期: T 组 FAIL(旁路), K 组保持现值。修后 0 失败=达标。
import importlib.util, os
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
W = r"D:\myagent\workspace\write-guard"
spec = importlib.util.spec_from_file_location("w", W + B + "handler.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
PDIR = "D:" + B + "myagent" + B + ".hermes" + B + "plugins" + B + "write-guard"
CFG  = "D:" + B + "myagent" + B + ".hermes" + B + "config.yaml"
WS   = "D:" + B + "myagent" + B + "workspace"
def call(cmd):
    r = m.on_pre_tool_call("terminal", {"command": cmd}, "pm")
    return "PASS" if r is None else str(r.get("action"))

cases = [
    # ---- 靶心 T：引号整包粘连目标选项旁路（当前 PASS=旁路，修后必须 hit）
    ("T1  cp \"-t<PDIR>/\" 尾斜杠",            f'cp ok.txt "-t{PDIR}/"',                          "hit"),
    ("T2  cp '-t<PDIR>' 无斜杠(缴械覆写链)",     f"cp ok.txt '-t{PDIR}'",                            "hit"),
    ("T3  install '-t<PDIR>/'",                f"install '-t{PDIR}/' ok.txt",                     "hit"),
    ("T4  dd \"of=<CFG>\"",                    f'dd "of={CFG}" if=ok.txt bs=1 count=4',           "hit"),
    ("T5  cp \"--target-directory=<CFG>\"",    f'cp "--target-directory={CFG}" ok.txt',           "hit"),
    ("T6  cp '-t=<PDIR>' 混粘",                f"cp '-t={PDIR}' ok.txt",                          "hit"),
    ("T7  bash -c 载体内引号包 -t",              'bash -c ' + chr(39) + f'cp ok.txt "-t{PDIR}/"' + chr(39), "hit"),
    ("T8  sort \"-t<PDIR>\" 反例锁门外?",        f'sort "-t{PDIR}" f',                              "any"),
    # ---- 锁形 K：修后不得回退/不得误拦
    ("K1  裸 -t<PDIR> (r7 已正确)",             f'cp ok.txt -t{PDIR}',                             "hit"),
    ("K2  dd of=<CFG> 裸 (已正确)",             f'dd of={CFG} if=ok.txt bs=1 count=4',             "hit"),
    ("K3  --target-dir= 裸等号",                f'cp --target-directory={CFG} ok.txt',             "hit"),
    ("K4  引号值 --target-dir=\"<CFG>\"",       f'cp --target-directory="{CFG}" ok.txt',           "hit"),
    ("K5  '-t' <DIR> 分列(F-7-2 登记面)",        f"cp '-t' {PDIR} ok.txt",                          "hit"),
    ("K6  curl \"-o<CFG>\" (r13 E1 不回潮)",     f'curl "-o{CFG}" http://x',                        "hit"),
    ("K7  cp \"-t<非保护 ws>\" 零误拦",           f'cp ok.txt "-t{WS}/x"',                            "pass"),
    ("K8  install -t<非保护>",                  f"install -t{WS}/y ok.txt",                        "pass"),
    ("K9  grep \"-o\" CFG 门外",                f'grep "-o" {CFG}',                                "pass"),
    ("K10 cp \"-t<PDIR>劈x\" 穿插族登记面",       f'cp "-t{PDIR[:6]}"x/{PDIR[6:]}\' ok.txt',           "any"),
    # ---- 靶心 T11~T18：质量路 Q13-A/B 引号 cluster + -t 族（当前 PASS=旁路，修后 hit）
    ("T11 curl \"-so\" <CFG> url (Q13-A)",       f'curl "-so" {CFG} http://x',                     "hit"),
    ("T12 curl \"-sSo\" <CFG> (Q13-A)",          f'curl "-sSo" {CFG} http://x',                    "hit"),
    ("T13 wget \"-qO\" <CFG> (Q13-A)",           f'wget "-qO" {CFG} http://x',                     "hit"),
    ("T14 sort \"-ro\" <CFG> (Q13-A)",           f'sort "-ro" {CFG} d.txt',                        "hit"),
    ("T15 cp \"-t<PDIR>\" (Q13-B=sec S1 同洞)",   f'cp ok.txt "-t{PDIR}"',                          "hit"),
    ("T16 cp \"-tdst\" 非保护对照 保持PASS",       'cp "-tdst" in2.txt',                             "any"),
    ("T17 bash -c 内 curl \"-so\" <CFG>",         "bash -c " + chr(39) + f'curl "-so" {CFG} http://x' + chr(39), "hit"),
    ("T18 curl \"-oL\" url 零误拦锁",             'curl "-oL" http://x',                            "pass"),
    ("K11 grep \"-so\" 词 门外零误拦",            f'grep "-so" {CFG}',                              "pass"),
]
nf = 0
for label, cmd, want in cases:
    got = call(cmd)
    okv = {"hit": got in ("approve", "block"), "pass": got == "PASS", "any": True}[want]
    nf += (not okv)
    print(f"{'ok ' if okv else 'FAIL'} {label:42s} -> {got:8s} want {want}")
print(f"通过 {len(cases)-nf} 失败 {nf} {[] if nf else '(有失败)'}")
