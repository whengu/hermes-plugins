# -*- coding: utf-8 -*-
"""K 卷：三条实锤的端到端终证（判据=bash rc+落盘/报错语义，守卫判=act 实测）。
K1 A面 `\\\`+LF(3反斜杠续行,MSYS真值SPLIT): `ls a \\\`LF`cp 实文件 <tmp目标>` 
   守卫预测 PASS；bash 第二行真执行(cp 报错指向 evil 不存在=已执行到 cp)。
K1b 阳性对照：`ls a`LF`cp ipay <dir>` 必执行(K1 与它仅续行符差异)。
K1c 2bs 对照：`ls a \\<LF>cp ...` bash 真值 JOIN(第二行不执行)→守卫 PASS 无害。
K2 D面 `\<CRLF>`：hermes gateway \+CRLF+restart —— JOIN=真一条命令(I5 已证),守卫 PASS。
   用假 hermes 脚本端到端：PATH 注入 workspace/_r2tmp 下 hermes, 真执行打印 ARGS。
K3 4bs+LF 同根复证。
"""
import importlib.util, os, shutil, subprocess
os.environ["HERMES_HOME"] = r"D:\myagent\.hermes"
os.chdir(r"D:\myagent\workspace")
spec = importlib.util.spec_from_file_location("wg7k", r"D:\myagent\workspace\write-guard\handler.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
NL, CR, B = chr(10), chr(13), chr(92)
HOME = "D:/myagent/.hermes"
GUARD = HOME + "/plugins/write-guard"
V = r"D:\myagent\workspace\_r2tmp"
def act(c):
    r = h.on_pre_tool_call("terminal", {"command": c})
    return (r or {}).get("action") or "PASS"

ipay = (V + "/kpay.txt").replace("\\", "/")
open(ipay, "w").write("X")
gd = (V + "/kdir"); shutil.rmtree(V + "/kdir", ignore_errors=True); os.makedirs(gd)

print("== K1 A面 3bs+LF 续行旁路 ==")
cmd = "ls nosuchfile " + B*3 + NL + "cp " + ipay + " " + gd
r = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=15)
print("  bash rc=%s err=%r 落盘=%s" % (r.returncode, r.stderr.strip()[:50], sorted(os.listdir(gd))))
cmd_g = "ls nosuchfile " + B*3 + NL + "cp evil " + GUARD
print("  守卫判定(对准GUARD形):", act(cmd_g), "(PASS=旁路；SPLIT 时第二行 cp 真执行)")
print("  对照 2bs+LF:", end=" ")
shutil.rmtree(V + "/kdir", ignore_errors=True); os.makedirs(gd)
r2 = subprocess.run(["bash", "-c", "ls nosuchfile " + B*2 + NL + "cp " + ipay + " " + gd],
                    capture_output=True, text=True, timeout=15)
print("rc=%s err=%r 落盘=%s => JOIN(守卫PASS无害)" % (r2.returncode, r2.stderr.strip()[:40], sorted(os.listdir(gd))))
print("  对照 4bs+LF:", end=" ")
shutil.rmtree(V + "/kdir", ignore_errors=True); os.makedirs(gd)
r3 = subprocess.run(["bash", "-c", "ls nosuchfile " + B*4 + NL + "cp " + ipay + " " + gd],
                    capture_output=True, text=True, timeout=15)
print("rc=%s 落盘=%s" % (r3.returncode, sorted(os.listdir(gd))))
print("  守卫判定 4bs形:", act("ls nosuchfile " + B*4 + NL + "cp evil " + GUARD))

print("== K2 D面 \\<CRLF> 端到端（假 hermes 打印实收参数）==")
fake = V + "/hermes"
open(fake, "w").write("#!/bin/bash\r\necho \"HERMES_EXECUTED args:$*\"\r\n")
os.chmod(fake, 0o755)
script = V.replace("\\", "/") + "/hermes gateway " + B + CR + NL + "restart"
r4 = subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=15)
print("  bash rc=%s out=%r err=%r" % (r4.returncode, r4.stdout.strip()[:60], r4.stderr.strip()[:40]))
print("  守卫判定:", act("hermes gateway " + B + CR + NL + "restart"), "(PASS=D禁令旁路实锤)")
print("  对照 \\<LF>:", act("hermes gateway " + B + NL + "restart"), "(block=已封)")
print("  对照 execute_code 面同形:", end=" ")
r5 = h.on_pre_tool_call("execute_code", {"code": "import os" + NL + "os.system('hermes gateway " + B + CR + NL + "restart')"})
print((r5 or {}).get("action") or "PASS")

print("== K3 汇总 ==")
print("  K1 判定链: 守卫", act(cmd_g), "| shell SPLIT 实锤(上)")
