# -*- coding: utf-8 -*-
"""G3 语义实证（名净化版）：bash 对各换行形的 SPLIT/JOIN 真值。"""
import os, subprocess
NL, CR, B = chr(10), chr(13), chr(92)
T = r"D:\myagent\workspace\_r2tmp"
os.makedirs(T, exist_ok=True)
def probe(idx, label, script):
    mkf = os.path.join(T, "m3_%02d" % idx)
    if os.path.exists(mkf): os.remove(mkf)
    script = script.replace("@MK", mkf.replace("\\", "/"))
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=15)
    print("  %-24s %-30r rc=%-3s marker=%-7s %s" % (
        label, script[:26], r.returncode,
        "CREATED" if os.path.exists(mkf) else "absent",
        (r.stderr or "").strip()[:40]))
probe(1, "POS bareLF",        "true" + NL + "touch @MK")
probe(2, "POS semicolon",     "true; touch @MK")
probe(3, "backslash+LF",      "true " + B + NL + "touch @MK")
probe(4, "2backslash+LF",     "true " + B*2 + NL + "touch @MK")
probe(5, "3backslash+LF",     "true " + B*3 + NL + "touch @MK")
probe(6, "4backslash+LF",     "true " + B*4 + NL + "touch @MK")
probe(7, "backslash+CRLF",    "true " + B + CR + NL + "touch @MK")
probe(8, "2backslash+CRLF",   "true " + B*2 + CR + NL + "touch @MK")
probe(9, "bareCR",            "true" + CR + "touch @MK")
probe(10, "cp仿 2bs+LF",      "ls /etc/hostname " + B*2 + NL + "cp /etc/hostname @MK")
probe(11, "cp仿 bareLF",      "ls /etc/hostname" + NL + "cp /etc/hostname @MK")
