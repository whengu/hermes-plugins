import importlib.util, os
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
spec = importlib.util.spec_from_file_location("wg", r"D:\myagent\workspace\write-guard\handler.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
CFG = "D:/myagent/.hermes/config.yaml"
def j(cmd):
    r = m._judge_terminal(cmd, "terminal")
    print("%-7s| %s" % (((r or {}).get("action")) or "PASS", cmd))
j('pwsh -Command "Set-Content ' + CFG + ' x"')
j("Set-Content " + CFG + " x")
j("pwsh Set-Content " + CFG + " x")
r = m._judge_terminal('pwsh -Command "Set-Content ' + CFG + ' x"', "terminal")
print(r)
