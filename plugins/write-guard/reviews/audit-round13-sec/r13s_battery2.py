
import importlib.util, os, re
os.environ["HERMES_HOME"] = r"D:\myagent\.hermes"
os.chdir(r"D:\myagent\workspace")
spec = importlib.util.spec_from_file_location("wg", r"D:\myagent\workspace\write-guard\handler.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
def act(cmd):
    r = h.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action") or "PASS"
HOME = "D:/myagent/.hermes"; CFG = HOME + "/config.yaml"; WS = "D:/myagent/workspace/x.txt"
GUARD = HOME + "/plugins/write-guard/"
print("norm quoted-path:", h._normalize_path('"' + CFG + '"', base="D:/myagent/workspace"))
cases = {
 "F1 cp evil '-tGUARD' glued-quoted": act("cp evil.txt '-t" + GUARD + "'"),
 "F2 cp evil \"--target-directory=GUARD\" (A6 dup)": act('cp evil.txt "--target-directory=' + HOME + '/plugins/write-guard"'.replace("' + HOME + '", HOME)),
 "F3 Copy-Item \"-Destination:CFG\" WS colon-quoted": act("Copy-Item \"-Destination:" + CFG + "\" " + WS),
 "F4 Tee-Object \"-LiteralPath:CFG\"": act('Tee-Object "-LiteralPath:' + CFG + '"'),
 "F5 curl -o \"CFG\" (opt bare val quoted)": act('curl -o "' + CFG + '" http://x'),
 "F6 dd of=\"CFG\"": act('dd of="' + CFG + '" if=/dev/null bs=1 count=0'),
 "F7 curl '-O=CFG'": act("curl '-O=" + CFG + "' http://x"),
 "F8 wget \"-O=CFG\"": act('wget "-O=' + CFG + '" http://x'),
 "F9 install '-tGUARD' evil": act("install '-t" + GUARD + "' evil.txt"),
 "F10 curl '-O' CFG quoted opt word r12 face": act("curl '-O' " + CFG + " http://x"),
 "F11 Tee -FilePath \"CFG\" x (quoted value ctrl)": act('Tee-Object -FilePath "' + CFG + '" x'),
 "F12 cp -t <GUARD> with leading space inside quotes '-t <GUARD>'": act("cp '-t " + GUARD + "' evil.txt"),
 "F13 pwsh -Command Copy-Item colon quoted": act('pwsh -Command "Copy-Item \\"-Destination:' + CFG + '\\" ' + WS + '"'),
 "F14 curl --output \"CFG\"": act('curl --output "' + CFG + '" http://x'),
}
for k, v in cases.items(): print(v.ljust(9), k)
