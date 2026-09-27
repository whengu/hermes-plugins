# -*- coding: utf-8 -*-
"""G' 语义实证：bash 对 \<LF> / \\<LF> / \<CRLF> / \\<CRLF> 到底切不切。
用 marker 文件判定：若 `true <bform>touch marker` 生成文件=换行是真分隔符（cp 会跑）；
无文件=续行粘连（cp 只是参数、不执行）。只写 workspace/_r2tmp，零受保护路径。"""
import os, subprocess
NL, CR, B = chr(10), chr(96*0+13) if False else chr(13), chr(92)
T = r"D:\myagent\workspace\_r2tmp"
os.makedirs(T, exist_ok=True)
def probe(name, sep):
    mk = os.path.join(T, "m_" + name)
    if os.path.exists(mk): os.remove(mk)
    script = "true " + sep + "touch " + mk.replace("\\", "/")
    subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=15)
    created = os.path.exists(mk)
    print("  %-22s repr=%-22r marker=%s => %s" % (
        name, sep, "CREATED" if created else "absent",
        "SPLIT(换行是真分隔)" if created else "JOINED(续行粘连)"))
probe("backslash+LF", B + NL)
probe("2backslash+LF", B*2 + NL)
probe("3backslash+LF", B*3 + NL)
probe("backslash+CRLF", B + CR + NL)
probe("2backslash+CRLF", B*2 + CR + NL)
probe("bare LF", NL)
probe("bare CR", CR)
# 复刻攻击面：若 SPLIT，则守卫 A3 (ls a \\<LF>cp evil GUARD→PASS) 为真旁路
mk = os.path.join(T, "m_cp_sim"); 
if os.path.exists(mk): os.remove(mk)
subprocess.run(["bash","-c","ls a " + B*2 + NL + "cp /etc/hostname " + mk.replace("\\","/")],
               capture_output=True, text=True, timeout=15)
print("  cp仿真实证 `ls a \\\\ <LF> cp src marker`: marker=%s" % ("CREATED→cp真的执行了" if os.path.exists(mk) else "absent"))
