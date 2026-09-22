# -*- coding: utf-8 -*-
"""fix-008 补充探针：整词包裹形现状 + _command_word 行为。"""
import importlib.util
import os

B = chr(92)
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
CFG = "D:/myagent/.hermes/config.yaml"
cases = [
    ("cp evil sq-G(整词包裹)", "cp evil " + SQ + G + SQ),
    ("cp evil dq-G", "cp evil " + Q + G + Q),
    ("cp sq-G2 out", "cp " + SQ + G + "/handler.py" + SQ + " out/"),
    ("cp x sq-CFG", "cp x " + SQ + CFG + SQ),
    ("cp '-t'=G x (对照勿扩)", "cp " + SQ + "-t" + SQ + "=" + G + " x"),
    ("tdir=ws (F-7-2 负例)", "cp '--target-directory'=D:/myagent/workspace/out x"),
]
for n, c in cases:
    print(n.ljust(24), "->", act("terminal", {"command": c}))
