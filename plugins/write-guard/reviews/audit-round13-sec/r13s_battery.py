
import importlib.util, os
os.environ["HERMES_HOME"] = r"D:\myagent\.hermes"
os.chdir(r"D:\myagent\workspace")
spec = importlib.util.spec_from_file_location("wg", r"D:\myagent\workspace\write-guard\handler.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
def act(cmd):
    r = h.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action") or "PASS"
HOME = "D:/myagent/.hermes"; CFG = HOME + "/config.yaml"; WS = "D:/myagent/workspace/x.txt"
cases = {
 "A1 curl \"--output=CFG\"": act('curl "--output=' + CFG + '" http://x'),
 "A2 curl '--output=CFG'": act("curl '--output=" + CFG + "' http://x"),
 "A3 wget \"--output-document=CFG\"": act('wget "--output-document=' + CFG + '" http://x'),
 "A4 curl \"-o=CFG\" (semantics=no write)": act('curl "-o=' + CFG + '" http://x'),
 "A5 dd \"of=CFG\"": act('dd "of=' + CFG + '" if=/dev/null bs=1 count=0'),
 "A6 cp \"--target-directory=GUARD\" evil": act('cp evil.txt "--target-directory=' + HOME + '/plugins/write-guard"'),
 "A7 cp --target-directory=GUARD evil (bare ctrl)": act('cp evil.txt --target-directory=' + HOME + '/plugins/write-guard'),
 "A8 curl --output=CFG (bare ctrl)": act('curl --output=' + CFG + ' http://x'),
 "A9 dd of=CFG (bare ctrl)": act('dd of=' + CFG + ' if=/dev/null bs=1 count=0'),
 "B1 curl \"-oCFG\" (E3 fixed ctrl)": act('curl "-o' + CFG + '" http://x'),
 "C1 Copy-Item -Destination:CFG": act("Copy-Item -Destination:" + CFG),
 "C2 Copy-Item -Destination:'CFG' ws": act("Copy-Item -Destination:'" + CFG + "' " + WS),
 "C3 -Destination:WS -Destination:CFG (glued Z1)": act("Copy-Item -Destination:" + WS + " -Destination:" + CFG),
 "C4 -Path:CFG -Destination WS": act("Copy-Item -Path:" + CFG + " -Destination " + WS),
 "C5 Tee -FilePath:CFG x": act("Tee-Object -FilePath:" + CFG + " x"),
 "C6 copy-item -destination:CFG (lower)": act("copy-item -destination:" + CFG),
 "C7 TAB sep -Destination CFG WS": act("Copy-Item\t-Destination\t" + CFG + "\t" + WS),
 "C8 -Destination CFG -WhatIf": act("Copy-Item -Destination " + CFG + " -WhatIf"),
 "C9 -Container WS -Path CFG -Destination WS2": act("Copy-Item -Container " + WS + " -Path " + CFG + " -Destination D:/myagent/workspace/y.txt"),
 "C10 -Destination:CFG -WhatIf": act("Copy-Item -Destination:" + CFG + " -WhatIf"),
 "C11 -Destination \"CFG\" -Container WS": act('Copy-Item -Destination "' + CFG + '" -Container ' + WS),
 "D1 pwsh \"Copy-Item -Destination:CFG -Path WS\"": act('pwsh -Command "Copy-Item -Destination:' + CFG + ' -Path ' + WS + '"'),
 "D2 pwsh \"Tee-Object -LiteralPath CFG\"": act('pwsh -Command "Tee-Object -LiteralPath ' + CFG + '"'),
 "D3 bash -c \"curl --output=CFG x\"": act('bash -c "curl --output=' + CFG + ' http://x"'),
 "D4 bash -c \"curl '-soCFG' x\"": act("bash -c \"curl '-so" + CFG + "' http://x\""),
 "D5 pwsh \"Set-Content -Path CFG\"": act('pwsh -Command "Set-Content -Path ' + CFG + ' -Value x"'),
 "E1 curl -O \"URL\" \"CFG\"": act('curl -O "http://x/a.zip" "' + CFG + '"'),
 "E2 curl \"https://x/oconfig.yaml\"": act('curl "https://x/oconfig.yaml"'),
 "E3 sort \"/o\" CFG": act('sort "/o" ' + CFG),
 "E4 grep \"-oCFG\" file (gate outside)": act('grep "-o' + CFG + '" f'),
 "E5 cp \"CFG\" \"BAK\" read": act('cp "' + CFG + '" "' + HOME + '/bak.yaml"'),
 "E6 curl \"-OJk\" http://x": act('curl "-OJk" http://x'),
}
for k, v in cases.items(): print(v.ljust(9), k)
