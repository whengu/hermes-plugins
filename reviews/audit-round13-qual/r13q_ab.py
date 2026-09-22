import importlib.util, os, sys
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
W = r"D:\myagent\workspace\write-guard"
CFG = "D:" + B + "myagent" + B + ".hermes" + B + "config.yaml"
CFGS = CFG.replace(B, "/")
WSX = "D:/myagent/workspace/x.txt"
CMD = "Copy-Item -Destination " + CFGS + " -Path " + WSX

for path, name in [(W + B + "_r2tmp" + B + "r13q" + B + "h_4e254c8.py", "oldA"),
                   (W + B + "_r2tmp" + B + "r13q" + B + "h_4e254c8.py", "oldB"),
                   (W + B + "handler.py", "newC")]:
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    r = m._judge_terminal(CMD, "terminal")
    print(name, "->", "PASS" if r is None else r.get("action"),
          "| has percmd:", hasattr(m, "_PS_TARGET_FLAGS"),
          "| norm_cfg:", m._normalize_path(CFGS, base=os.getcwd()))
