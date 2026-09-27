# round11 施工期形态矩阵实测（TC 预期值唯一依据，验收后可留档）
import importlib.util, os
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
spec = importlib.util.spec_from_file_location("wg11m", os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "handler.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
CFG = "D:/myagent/.hermes/config.yaml"
WS = "D:/myagent/workspace/a.txt"
GD = "D:" + B + "myagent" + B + ".hermes" + B + "plugins" + B + "write-guard"


def j(c):
    r = m.on_pre_tool_call("terminal", {"command": c})
    return (r or {}).get("action") or "PASS"

tests = [
    ("前置漏拦封堵", "Copy-Item -Destination " + CFG + " " + WS),
    ("Tee前置封堵", "Tee-Object -FilePath " + CFG + " -InputObject x"),
    ("载体封堵", 'pwsh -Command "Copy-Item -Destination ' + CFG + " " + WS + '"'),
    ("sudo载体封堵", 'sudo pwsh -Command "Copy-Item -Destination ' + CFG + " " + WS + '"'),
    ("反向误弹归正", "Copy-Item -Destination " + WS + " " + CFG),
    ("尾位锁形", "Copy-Item evil.txt -Destination " + CFG),
    ("双标志源位B锁", "Copy-Item -Container " + CFG + " -Destination " + WS),
    ("守卫前置封堵", "Copy-Item -Destination " + GD + " " + WS),
    ("引号标志形", 'Copy-Item "-Destination" ' + CFG + " " + WS),
    ("小写cmdlet+flag", "copy-item -destination " + CFG + " " + WS),
    ("反斜杠CFG", "Copy-Item -Destination " + CFG.replace("/", B) + " " + WS),
    ("cd链式", "cd D:" + B + "myagent" + "; Copy-Item -Destination " + CFG + " " + WS),
    ("Set-Content不回潮", "Set-Content -Path " + CFG + " -Value x"),
    ("Get-Content负例", "Get-Content -Path " + CFG),
    ("cp源零差", "cp " + CFG + " " + WS),
    ("cp目标正例", "cp " + WS + " " + CFG),
    ("sort -o回潮锁", "sort -o " + CFG + " d.txt"),
    ("sort /O锁", "sort /O " + CFG + " d.txt"),
    ("sort ws/o归正", "sort D:/myagent/workspace/o " + CFG),
    ("curl url-o归正", "curl http://x/o " + CFG),
    ("wget url-o归正", "wget http://x/f/o " + CFG),
    ("附录⑥归正", "sort D:/myagent/workspace/my-dir-o " + CFG),
    ("cluster粘连锁", "curl -sSL -o" + CFG + " http://x"),
    ("curl -O URL红线", "curl -O http://x/a.zip"),
    ("tee CFG out2锁", "tee " + CFG + " out2.txt"),
    ("Path源Dest目标", "Copy-Item -Path " + WS + " -Destination " + CFG),
    ("LiteralPath前置", "Copy-Item -LiteralPath " + CFG + " -Destination " + WS),
    ("rsync源零差", "rsync -av " + CFG + " " + WS),
    ("LiteralPath前置仅", "Copy-Item -LiteralPath " + CFG + " " + WS),
    ("Container前置仅", "Copy-Item -Container " + CFG + " " + WS),
    ("Path前置仅", "Copy-Item -Path " + CFG + " " + WS),
    ("引号标志", 'Copy-Item "-Destination" ' + CFG + " " + WS),
    ("dest带引号值", "Copy-Item -Destination " + chr(34) + CFG + chr(34) + " " + WS),
]
for tag, cmd in tests:
    print(tag.ljust(18) + ":", j(cmd))
