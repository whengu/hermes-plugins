
import importlib.util, os
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
CMDS = [
    "bash -c 'hermes gateway restart'",
    "cmd /c hermes gateway run",
    "pwsh -Command \"hermes gateway restart\"",
    "powershell -c 'hermes gateway restart'",
    "sh -c \"hermes gateway restart && echo ok\"",
    "hermes  gateway  restart",
    "hermes\tgateway restart",
    "hermes gateway restart; hermes gateway status",
    "git status && hermes gateway restart",
    "export A=1 && hermes gateway run",
    "& hermes gateway restart",
    "hermes.exe gateway run",
]
for gen in ("handler_r18", "handler_r12era"):
    spec = importlib.util.spec_from_file_location(gen, "D:" + B + "myagent" + B + "workspace" + B + "write-guard" + B + "reviews" + B + "fix018-scratch" + B + gen + ".py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    print("==", gen)
    for c in CMDS:
        r = m.on_pre_tool_call("terminal", {"command": c}, "pm")
        v = "PASS" if r is None else str(r.get("action"))
        print(f"  {v:8s} {c[:64]!r}")
