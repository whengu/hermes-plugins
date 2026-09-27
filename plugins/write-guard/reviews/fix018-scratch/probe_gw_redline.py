# PM 探针：hermes gateway restart / run 各族形的处置（block=直接拦截, approve=弹卡, PASS=放行）
# 双代对拍：round18 当代 (d727594) vs gateway 进程实际加载的 9-22 22:41 部署代
import importlib.util, os
B = chr(92)
SC = "D:" + B + "myagent" + B + "workspace" + B + "write-guard" + B + "reviews" + B + "fix018-scratch"
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")

CMDS = [
    "hermes gateway restart",
    "hermes gateway run",
    "hermes gateway stop",
    "hermes gateway status",
    "hermes.exe gateway restart",
    "D:" + B + "Project" + B + "guwh" + B + "hermes-agent" + B + "venv" + B + "Scripts" + B + "hermes.exe gateway restart",
    "hermes gateway restart --force",
    "sudo hermes gateway restart",
    "hermes gateway",
]
for gen, path in (("round18-HEAD", SC + B + "handler_r18.py"),
                  ("gateway-loaded-era", "D:" + B + "myagent" + B + ".hermes" + B + "plugins" + B + "write-guard" + B + "handler.py")):
    spec = importlib.util.spec_from_file_location(gen, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    print("==", gen)
    for c in CMDS:
        r = m.on_pre_tool_call("terminal", {"command": c}, "pm")
        v = "PASS" if r is None else str(r.get("action"))
        msg = "" if r is None else str(r.get("message", ""))[:50]
        print(f"  {v:8s} {c[:70]}  {msg}")
