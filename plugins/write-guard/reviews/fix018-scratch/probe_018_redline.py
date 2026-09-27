# PM 红线复验 v2（round18 收线批）——临时目录引用族命中时打印 hit 证据
import importlib.util, os
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
spec = importlib.util.spec_from_file_location("hg18", "D:" + B + "myagent" + B + "workspace" + B + "write-guard" + B + "handler.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
def t(cmd):
    r = m.on_pre_tool_call("terminal", {"command": cmd}, "pm")
    if r is None: return "PASS", ""
    return str(r.get("action")), str(r.get("message", ""))[:90]
CFG = "D:" + B + "myagent" + B + ".hermes" + B + "config.yaml"
checks = [
    ("gateway restart 按设计拦截", "hermes gateway restart", ("approve", "block")),
    ("cp 真配置弹卡", f"cp evil {CFG}", ("approve",)),
    ("Copy-Item 源位读放行", f"Copy-Item {CFG} D:" + B + "other" + B + "x.yaml", ("PASS",)),
    ("Copy-Item -Destination 弹卡", "Copy-Item D:" + B + "other" + B + "x.yaml -Destination " + CFG, ("approve",)),
    ("临时目录引用族命中(守卫正常面)", "cp a " + B + "tmp" + B + "b", ("block",)),
    ("紧邻 -t 别名目标 hit", "cp -t ~/.hermes/out/ s1 s2", ("approve",)),
    ("cluster -rt 紧邻 hit（-t 绑 tilde 目标位）", "cp -rt ~/.hermes/logs s1", ("approve",)),
    ("cluster -rt 后随位=源读（-t 已绑 s1）", "cp -rt s1 ~/.hermes/logs", ("PASS",)),
    ("mv 绝对改名红线维持(别名目标弹,绝对末位在清单=hit)", "mv D:" + B + "other" + B + "a.txt ~/.hermes/config.yaml", ("approve",)),
]
bad = 0
for name, cmd, wants in checks:
    v, msg = t(cmd)
    ok = v in wants
    print(("ok  " if ok else "FAIL"), name, "->", v, "|", msg if not ok else "")
    if not ok: bad += 1
print("REDLINE:", "ALL-OK" if bad == 0 else f"{bad} BAD")
