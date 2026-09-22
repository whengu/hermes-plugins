import importlib.util, os, sys
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
W = r"D:\myagent\workspace\write-guard"
CFG = "D:" + B + "myagent" + B + ".hermes" + B + "config.yaml"
CFGS = CFG.replace(B, "/")
spec = importlib.util.spec_from_file_location("wg", W + B + "handler.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
def j(cmd):
    r = m._judge_terminal(cmd, "terminal")
    return "PASS" if r is None else str(r.get("action"))
CASES = [
    # quoted cluster(-options ending o) + space value — pre-existing combination face
    ("curl \"-so\" CFG url", 'curl "-so" ' + CFGS + ' http://x'),
    ("curl \"-sSo\" CFG url", 'curl "-sSo" ' + CFGS + ' http://x'),
    ("curl -sSo CFG url (unquoted ctrl)", "curl -sSo " + CFGS + " http://x"),
    ("wget \"-qO\" CFG url", 'wget "-qO" ' + CFGS + ' http://x'),
    ("sort \"-ro\" CFG d (unquoted d4 ctrl)", 'sort "-ro" ' + CFGS + " d.txt"),
    ("sort -ro CFG d (unquoted)", "sort -ro " + CFGS + " d.txt"),
    # quoted whole-word non-write option + CFG as url: PASS should be correct
    ("curl \"-oL\" CFG url", 'curl "-oL" ' + CFGS + " http://x"),
    # equal-glued quoted value in PS gn face
    ("Copy -Destination:=\"CFG\" ws", 'Copy-Item -Destination:="' + CFGS + '" D:/myagent/workspace/x.txt'),
    # E face neighbors: quoted cluster with gluing inside double quotes with escaped content out-of-scope
    ("curl '-so' CFGS (single q)", "curl '-so" + CFGS + "' http://x"),
]
for name, cmd in CASES:
    print(f"{name:45s} -> {j(cmd)}")
