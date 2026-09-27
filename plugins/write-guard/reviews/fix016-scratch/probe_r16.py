# round16 预研探针：基线行为事实（改前必读）
import importlib.util, os
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
W = r"D:\myagent\workspace\write-guard"
spec = importlib.util.spec_from_file_location("w", W + B + "handler.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
CFG = "D:" + B + "myagent" + B + ".hermes" + B + "config.yaml"
WS = "D:" + B + "myagent" + B + "workspace"

def call(cmd):
    r = m.on_pre_tool_call("terminal", {"command": cmd}, "pm")
    return "PASS" if r is None else str(r.get("action"))

def call2(tool, args):
    r = m.on_pre_tool_call(tool, args, "pm")
    return "PASS" if r is None else str(r.get("action"))

print("-- terminal 绝对形 mv/cp 语义事实")
print("A1 mv x CFG_abs      ", call("mv " + WS + "/x " + CFG))
print("A2 mv CFG_abs x      ", call("mv " + CFG + " " + WS + "/x"))
print("A3 cp x CFG_abs      ", call("cp evil " + CFG))
print("A4 ren CFG_abs x     ", call("ren " + CFG + " " + WS + "/x"))
print("A5 echo> CFG_abs     ", call("echo x > " + CFG))
print("A6 tee CFG_abs       ", call("tee " + CFG))
print("A7 sed -i guard.py   ", call("sed -i 's/a/b/' D:" + B + "myagent" + B + ".hermes" + B + "plugins" + B + "write-guard" + B + "handler.py"))
print("A8 -t abs glued      ", call('cp "-tD:' + B + 'myagent' + B + '.hermes' + B + 'plugins' + B + 'write-guard" x'))
print("A9 curl -o abs glued ", call('curl "-oD:' + B + 'myagent' + B + '.hermes' + B + 'config.yaml" url'))
print("-- write_file / execute_code tilde 面基线")
print("B1 wf ~/.hermes/cfg  ", call2("write_file", {"path": "~/.hermes/config.yaml", "content": "x"}))
print("B2 wf C:/u/.hermes   ", call2("write_file", {"path": "C:/Users/guwh/.hermes/config.yaml", "content": "x"}))
print("B3 wf HOME env       ", call2("write_file", {"path": "$HOME/.hermes/config.yaml", "content": "x"}))
print("B4 ec open tilde w   ", call2("execute_code", {"code": "open('~/.hermes/config.yaml','w')"}))
print("B5 ec shutil tilde   ", call2("execute_code", {"code": "shutil.copy('a','~/.hermes/config.yaml')"}))
print("B6 ec PATH tilde     ", call2("execute_code", {"code": "Path('~/.hermes/config.yaml').write_text('x')"}))
print("-- tilde/别名 terminal 基线（应为 PASS=旁路）")
print("C1 cp tilde          ", call("cp evil ~/.hermes/config.yaml"))
print("C2 cat tilde         ", call("cat ~/.hermes/config.yaml"))
print("C3 tilde dir cp      ", call("cp evil ~/.hermes"))
print("C4 HOME=undefined    ", "HOME=", repr(os.environ.get("HOME")))
print("C5 norm tilde raw    ", m._normalize_path("~/.hermes/config.yaml"))
print("C6 norm $HOME raw    ", m._normalize_path("$HOME/.hermes/config.yaml"))
print("C7 norm alias abs    ", m._normalize_path("C:/Users/guwh/.hermes/config.yaml"))
print("C8 hermes_home norm  ", m._hermes_home())
