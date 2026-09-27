import importlib.util, os
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
spec = importlib.util.spec_from_file_location("wg", r"D:\myagent\workspace\write-guard\handler.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
CFG = "D:/myagent/.hermes/config.yaml"
GD = "D:/myagent/.hermes/plugins/write-guard"
TD = "--target-directory"
SQ, DQ = chr(39), chr(34)
def j(cmd):
    r = m._judge_terminal(cmd, "terminal")
    print("%-7s| %s" % (((r or {}).get("action")) or "PASS", cmd))
j("cp -" + DQ + "t" + DQ + GD + " evil")
j("cp -" + DQ + TD + DQ + "=" + GD + " x")
j("cp -" + SQ + TD + SQ + "=" + GD + " x")
j("cp " + SQ + "-t" + SQ + " " + CFG + " out/")
j("cp -" + DQ + TD + DQ + " " + GD + " evil")
