import importlib.util, os
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
spec = importlib.util.spec_from_file_location("wg", r"D:\myagent\workspace\write-guard\handler.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
CFG = "D:" + B + "myagent" + B + ".hermes" + B + "config.yaml"
HD  = "D:" + B + "myagent" + B + ".hermes" + B + "plugins" + B + "write-guard" + B + "handler.py"
GD  = "D:" + B + "myagent" + B + ".hermes" + B + "plugins" + B + "write-guard"
WS  = "D:" + B + "myagent" + B + "workspace" + B + "a.txt"
def act(tool, args):
    if tool == "terminal":
        return m._judge_terminal(args.get("command", ""), "terminal")
    return None  # 本批场景均为 terminal
def j(tool, args):
    r = act(tool, args); return "approve" if r else "PASS"
print("== S-1 ==")
print("1a", j("terminal", {"command": "curl -o" + CFG.replace(B, "/") + " http://x"}))
print("1b", j("terminal", {"command": "curl -sSL -o" + HD.replace(B, "/") + " http://x"}))
print("1c", j("terminal", {"command": "sort -o" + CFG.replace(B, "/") + " d.txt"}))
print("1d NEG -o spaced", j("terminal", {"command": "curl -o " + CFG.replace(B, "/") + " http://x"}))
print("== S-2 ==")
print("2a", j("terminal", {"command": 'pwsh -Command "Copy-Item evil ' + CFG.replace(B, "/") + '"'}))
print("2b", j("terminal", {"command": 'pwsh -Command "Tee-Object -FilePath ' + CFG.replace(B, "/") + '"'}))
print("2c ctrl Set-Content", j("terminal", {"command": 'pwsh -Command "Set-Content ' + CFG.replace(B, "/") + ' x"'}))
print("== S-3 ==")
print("3a", j("terminal", {"command": "echo x & cp evil " + GD.replace(B, "/")}))
print("3b", j("terminal", {"command": "echo x > " + WS + " & cp evil " + GD.replace(B, "/")}))
print("3c ctrl &&", j("terminal", {"command": "echo x && cp evil " + GD.replace(B, "/")}))
print("3d FP 2>&1", j("terminal", {"command": "type f 2>&1 > " + WS}))
print("3e FP echo x > NUL", j("terminal", {"command": "echo x > NUL"}))
print("== S-4 ==")
print("4a", j("terminal", {"command": "runas /user:admin cp evil " + GD.replace(B, "/")}))
print("4b", j("terminal", {"command": "sudo cp evil " + GD.replace(B, "/")}))
print("4c", j("terminal", {"command": "LANG=C cp evil " + GD.replace(B, "/")}))
print("4d ctrl bare", j("terminal", {"command": "cp evil " + GD.replace(B, "/")}))
print("4e NEG env|grep", j("terminal", {"command": "env | grep config"}))
print("== S-5 ==")
print("5a", j("terminal", {"command": "cmd /c copy evil " + CFG.replace(B, "/")}))
print("5b", j("terminal", {"command": "cmd /q /c copy evil " + CFG.replace(B, "/")}))
print("5c", j("terminal", {"command": "pwsh -Command Copy-Item evil " + CFG.replace(B, "/")}))
print("5d ctrl quoted", j("terminal", {"command": 'cmd /c "copy evil ' + CFG.replace(B, "/") + '"'}))
print("5e NEG cmd /c dir", j("terminal", {"command": "cmd /c dir D:" + B + "myagent" + B + "workspace"}))
print("5f NEG pwsh -Command Get-Date", j("terminal", {"command": "pwsh -Command Get-Date"}))
