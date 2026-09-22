# -*- coding: utf-8 -*-
"""G' 对照组：证明 marker 探针本身可靠（已知 SPLIT 形必须 CREATED），再判疑形。"""
import os, subprocess
NL, CR, B = chr(10), chr(13), chr(92)
T = r"D:\myagent\workspace\_r2tmp"
os.makedirs(T, exist_ok=True)
def probe(name, script):
    mk = os.path.join(T, "m2_" + name).replace("\\", "/")
    p = os.path.join(T, "m2_" + name)
    if os.path.exists(p): os.remove(p)
    script = script.replace("@MK", mk)
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=15)
    print("  %-26s rc=%s marker=%-7s stderr=%r" % (
        name, r.returncode, "CREATED" if os.path.exists(p) else "absent",
        (r.stderr or "")[:48]))
probe("POS bareLF",  "true" + NL + "touch @MK")
probe("POS semi",    "true; touch @MK")
probe("NEG backslash+LF",   "true " + B + NL + "touch @MK")
probe("NEG 2backslash+LF",  "true " + B*2 + NL + "touch @MK")
probe("?? 3backslash+LF",   "true " + B*3 + NL + "touch @MK")
probe("?? backslash+CRLF",  "true " + B + CR + NL + "touch @MK")
probe("?? 2backslash+CRLF", "true " + B*2 + CR + NL + "touch @MK")
probe("?? bareCR",          "true" + CR + "touch @MK")
probe("?? CR-only",         "true" + CR + "touch @MK" + NL)
probe("cp仿 2bs+LF",  "ls a " + B*2 + NL + "cp /etc/hostname @MK")
probe("cp仿 3bs+LF",  "ls a " + B*3 + NL + "cp /etc/hostname @MK")
