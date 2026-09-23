# round16 探针 2：修复后消息面/载体面/处置分流核对
import importlib.util, os
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
W = r"D:\myagent\workspace\write-guard"
spec = importlib.util.spec_from_file_location("w", W + B + "handler.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def call(tool, args):
    r = m.on_pre_tool_call(tool, args, "pm")
    return r

r = call("terminal", {"command": "cp evil C:/Users/guwh/.hermes/config.yaml"})
print("T8:", r["action"], "|", r["message"].splitlines()[1] if "\n" in r["message"] else r["message"])
print("T8 rule_key:", r["rule_key"])
r = call("terminal", {"command": "cp evil ~/.hermes/config.yaml"})
print("T1:", r["action"])
r = call("terminal", {"command": "mv x ~/.hermes/config.yaml"})
print("K3:", r["action"])
r = call("terminal", {"command": "mv x C:/Users/guwh/.hermes/config.yaml"})
print("K3b mv 别名绝对目标:", r["action"])
r = call("terminal", {"command": "ren x ~/.hermes/config.yaml"})
print("ren 别名目标:", r["action"])
for tool, args, label in [
    ("write_file", {"path": "~/.hermes/config.yaml", "content": "x"}, "wf tilde"),
    ("write_file", {"path": "C:/Users/guwh/.hermes/config.yaml", "content": "x"}, "wf 别名绝对"),
    ("write_file", {"path": r"~\.hermes\plugins\write-guard\handler.py", "content": "x"}, "wf tilde 守卫源"),
    ("execute_code", {"code": "shutil.copy('a','~/.hermes/config.yaml')"}, "ec shutil tilde"),
    ("execute_code", {"code": "open('~/.hermes/config.yaml','w')"}, "ec open tilde"),
    ("execute_code", {"code": "Path('~/.hermes/config.yaml').write_text('x')"}, "ec Path tilde"),
    ("execute_code", {"code": "os.system(\"cp evil ~/.hermes/config.yaml\")"}, "ec os.system tilde"),
    ("execute_code", {"code": "subprocess.run(['cp','evil','C:/Users/guwh/.hermes/config.yaml'])"}, "ec subprocess 别名"),
]:
    r = call(tool, args)
    print(label, "->", "PASS" if r is None else r["action"])
r = call("terminal", {"command": "bash -c 'cp evil ~/.hermes/config.yaml'"})
print("载体内 tilde:", "PASS" if r is None else r["action"])
r = call("terminal", {"command": "cmd /c copy evil %USERPROFILE%\\.hermes\\config.yaml"})
print("cmd 载体 %USERPROFILE%:", "PASS" if r is None else r["action"])
# 展示消息的 norm 路径应是真实 home（视图一致），rule_key 也用视图 norm
r = call("terminal", {"command": "cp evil ~/.hermes/config.yaml"})
print("T1 rule_key:", r["rule_key"])
