# round8 安全路探针 E：fd 重定向 / & 重定向 / 包装词 / verbatim / 大小写参数 / -O FP
import importlib.util, os
spec = importlib.util.spec_from_file_location("hg", "handler.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
CFG = "D:/myagent/.hermes/config.yaml"
CFGW = "D:\\myagent\\.hermes\\config.yaml"
GUARD = "D:/myagent/.hermes/plugins/write-guard"
HANDW = "D:\\myagent\\.hermes\\plugins\\write-guard\\handler.py"

def term(cmd):
    r = h.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action", "PASS")

def wf(p):
    r = h.on_pre_tool_call("write_file", {"path": p})
    return (r or {}).get("action", "PASS")

cases = [
    "python x.py 2> " + CFG,
    "python x.py 2>" + CFG,
    "python x.py 1> " + CFG,
    "echo x &> " + CFG,
    "echo x &>" + CFGW,
    "echo x >NUL & cp evil " + GUARD,        # & 链式 + 守卫目录
    "echo x & cp evil " + GUARD,             # cmd 单 & 链接
    "sudo cp evil " + GUARD,
    "env cp evil " + GUARD,
    "time cp evil " + GUARD,
    "cmd /c cp evil " + GUARD,
    "cmd.exe /c copy evil " + HANDW,
    "pwsh -NoProfile -Command Copy-Item evil " + CFG,
    "pwsh -Command \"cp evil " + GUARD + "\"",
    "cp evil \\\\\\\\?\\\\" + CFGW,          # verbatim \\?\ 裸形
    "cp evil " + GUARD.replace("write-guard", "WRITE-GUARD"),
    "tee -a " + HANDW,                        # 管道首段 tee -a 守卫源码
    "curl -O " + CFG + " http://x",           # curl -O FP 向观察
    "wget -O " + CFG + " http://x",
]
for c in cases:
    print(f"[{term(c):7s}] {c!r}")
for p in [CFG, CFG.replace("config", "CONFIG"), "D:\\MYAGENT\\.HERMES\\plugins\\write-guard\\plugin.yaml",
          "D:/myagent/.hermes/plugins//write-guard/../write-guard/handler.py"]:
    print(f"[{wf(p):7s}] write_file {p!r}")
