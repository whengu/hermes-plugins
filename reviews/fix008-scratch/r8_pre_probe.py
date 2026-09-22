# -*- coding: utf-8 -*-
"""fix-008 前基线行为探针（PM 实测复核，只读判定，零磁盘写）。"""
import importlib.util
import os

B = chr(92)
NL, CR = chr(10), chr(13)
SQ, Q = chr(39), chr(34)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
spec = importlib.util.spec_from_file_location("wg", "write-guard" + B + "handler.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)


def act(t, a):
    r = h.on_pre_tool_call(t, a)
    return (r or {}).get("action") or "PASS"


G = "D:/myagent/.hermes/plugins/write-guard"
cases = [
    ("真续行 LF", "cp evil " + B + NL + G),
    ("真续行 CRLF", "cp evil " + B + CR + NL + G),
    ("单引号内 bs+LF", "echo " + SQ + "a" + B + NL + "cp evil " + G + SQ),
    ("双引号内 bs+LF", "echo " + Q + "a" + B + NL + G + Q),
    ("2bs+LF 分段后 cp", "echo a" + B + B + NL + "cp evil " + G),
    ("3bs+LF", "cp evil " + B * 3 + NL + G),
    ("4bs+LF", "cp evil " + B * 4 + NL + G),
    ("tdir 引号=粘连 sq", "cp " + SQ + "--target-directory" + SQ + "=" + G + " x"),
    ("tdir 引号=粘连 dq", "cp " + Q + "--target-directory" + Q + "=" + G + " x"),
    ("tdir 引号包整词含=路径", "cp " + SQ + "--target-directory=" + G + SQ + " x"),
    ("对照 -t sq 粘连=", "cp " + SQ + "-t" + SQ + "=" + G + " evil"),
    ("穿插 -'t'G", "cp -" + SQ + "t" + SQ + G + " evil"),
    ("半混 -dq tdir 空格", "cp -" + Q + "target-directory" + Q + " " + G + " evil"),
    ("gateway CRLF 续行", "hermes gateway " + B + CR + NL + "restart"),
    ("gateway LF 续行", "hermes gateway " + B + NL + "restart"),
    ("反引号混排", "echo a" + B + NL + "`cp evil " + G + "`"),
]
for n, c in cases:
    print(n.ljust(22), "->", act("terminal", {"command": c}))
