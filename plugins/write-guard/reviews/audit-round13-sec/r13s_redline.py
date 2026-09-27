
import importlib.util, os
os.environ["HERMES_HOME"] = r"D:\myagent\.hermes"
os.chdir(r"D:\myagent\workspace")
spec = importlib.util.spec_from_file_location("wg", r"D:\myagent\workspace\write-guard\handler.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
def act(cmd):
    r = h.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action") or "PASS"
HOME = "D:/myagent/.hermes"; CFG = HOME + "/config.yaml"; W = "D:/myagent/workspace"
GUARD = HOME + "/plugins/write-guard"; HD = GUARD + "/handler.py"
print("R1 gateway restart:", act("hermes gateway restart"), "(want block)")
print("R2 rm -rf home-plugins:", act("rm -rf " + HOME + "/plugins"), "(want block)")
print("R3 cp evil HD:", act("cp evil " + HD), "(want approve)")
print("R4 mv a b:", act("mv a.txt b.txt"), "(info: move family OOS)")
print("R5 Copy-Item src-read CFG->BAK(ws):", act("Copy-Item " + CFG + " " + W + "/bak.yaml"), "(want PASS)")
print("R6 Copy-Item -Destination CFG WS:", act("Copy-Item -Destination " + CFG + " " + W + "/x.txt"), "(want hit)")
print("X7 cp x \"-t<HD-dir-with-file-name>\" disarm:", act('cp handler.py "-t' + GUARD + '"'), "(PASS=bypass)")
print("X8 dd quoted of=HD disarm:", act('dd "of=' + HD + '" if=src.txt bs=1 count=4'), "(PASS=bypass)")
print("X9 dd bare of=HD ctrl:", act("dd of=" + HD + " if=src.txt bs=1 count=4"), "(want block)")
print("X10 cp \"--target-directory\"=GUARD (F-7-2 quoted opt+glued =):", act('cp "--target-directory"=' + GUARD + ' evil.txt'))
print("X11 cp '-t' split ctrl:", act("cp '-t' " + GUARD + " evil.txt"), "(want approve)")
print("X12 cp evil \"-t<ws non-protect>\" FP check:", act('cp evil.txt "-t' + W + '/td"'), "(want PASS no-FP)")
print("X13 echo > cfg ctrl:", act("echo x > " + CFG), "(want block)")
print("X14 cp \"-t" + GUARD + "\" via pwsh carrier:", act('pwsh -Command "cp evil.txt \\"-t' + GUARD + '\\""'))
print("X15 bash -c glue quoted:", act('bash -c "cp \\"-t' + GUARD + '\\" evil.txt"'))
