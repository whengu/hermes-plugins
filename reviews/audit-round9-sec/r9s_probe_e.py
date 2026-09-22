# round9 安全路探针 E：红线保持核查（gateway block / rm -r 平台层 / cp 写配置弹卡）
# + 写工具入口 + 名实/登记边界抽查
import importlib.util, os
os.environ["HERMES_HOME"] = "D:" + chr(92) + "myagent" + chr(92) + ".hermes"
os.chdir("D:" + chr(92) + "myagent" + chr(92) + "workspace")
HG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "handler.py")
spec = importlib.util.spec_from_file_location("hg", HG)
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
BS, q1, q2 = chr(92), chr(39), chr(34)
HOME = "D:/myagent/.hermes"
CFG = HOME + "/config.yaml"
CFGW = HOME.replace("/", BS) + BS + "config.yaml"
GUARD = HOME + "/plugins/write-guard"
HD = GUARD + "/handler.py"
WS = "D:/myagent/workspace/a.txt"
BAK = "D:/myagent/workspace/config.bak.yaml"

def term(cmd):
    r = h.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action", "PASS")

def gw(cmd):
    r = h._guard_gateway_cmd("terminal", {"command": cmd}, "t")
    return (r or {}).get("action", "PASS")

def wf(p, tool="write_file"):
    r = h.on_pre_tool_call(tool, {"path": p})
    return (r or {}).get("action", "PASS")

def run(group, cases, judge=term):
    print("---", group, "---")
    for c in cases:
        print(f"[{judge(c):7s}] {c!r}")

# 红线 1：gateway restart block（含 S-4/S-5/S-3 改动交叉后仍须 block）
run("RL1 gateway (gw)", [
    "hermes gateway restart",
    "hermes gateway run",
    "hermes gateway start",
    "sudo hermes gateway restart",                         # S-4 wrapper 不影响 D 守卫
    "bash -c " + q2 + "hermes gateway restart" + q2,       # 载体内嵌
    "cmd /c hermes gateway restart",                       # S-5 裸形交叉
    "echo x & hermes gateway restart",                     # S-3 单&交叉
    "hermes gateway " + BS + chr(10) + "restart",
], gw)
# 红线 1b：非禁动词不误伤
run("RL1b gateway neg (gw)", [
    "hermes gateway status",
    "hermes gateway stop",                                 # 决策：stop 不在禁令
    "git push --force",                                    # 永不白名单=框架层职责, 插件 PASS
], gw)
# 红线 2：rm -r 族属平台层 approvals 职责，插件四守卫不扩（PASS=分层正确）
run("RL2 rm -r platform-layer", [
    "rm -r " + GUARD,
    "rm -rf " + HOME,
    "sudo rm -rf " + GUARD,
    "rd /s /q " + GUARD.replace("/", BS),
])
# 红线 3：cp 写配置弹审批（approve），改名/复制（源位）不拦
run("RL3 cp config approve", [
    "cp evil " + CFG,
    "cp " + q2 + WS + q2 + " " + CFG,
    "copy " + WS + " " + CFG,
    "install -t " + HOME + " " + WS,
    "sh -c " + q2 + "cp evil " + CFG + q2,                 # 内嵌 cp 仍 approve 分流
    "cmd /c copy evil " + CFG,                             # S-5 裸形分流=approve 非 block
    "cp " + CFG + " " + BAK,                               # 源位=读 不拦
    "mv x " + GUARD,                                       # 改名族不拦
])
# 红线 3b：非 cp 写配置=block（必须走 skill）
run("RL3b non-cp block", [
    "echo x > " + CFG,
    "python x.py 2> " + CFG,                               # 非复制族重定向 → block
    "sed -i s/a/b/ " + CFG,
])
# 写工具入口红线
print("--- RL4 write_file/patch ---")
for p in [CFG, HD, HOME + "/plugins/write-guard/plugin.yaml",
          "D:" + BS + "MYAGENT" + BS + ".HERMES" + BS + "config.yaml",
          HOME + "/plugins//write-guard/../write-guard/handler.py",
          WS, BAK]:
    print(f"[{wf(p):7s}] write_file {p!r}")
print(f"[{wf(HD, 'patch'):7s}] patch handler")
print(f"[{wf(WS, 'patch'):7s}] patch workspace neg")
# 名实抽查：登记在案边界形态（期望与登记一致；不一致=名实不符候选）
run("NA registered-boundaries", [
    "sudo -u root cp evil " + GUARD,                       # 登记: PASS
    "pwsh -Command " + q2 + "tee evil " + CFG + q2,        # PS 别名 tee 登记: 走 shell 链观察
    "cp -" + q1 + "t" + q1 + GUARD + " evil",              # 劈 token 登记: PASS
    "cp evil " + q2 + BS + BS + "?"+ BS + CFGW + q2,       # verbatim 引号内登记族
    "robocopy D:/myagent/workspace " + HOME + " config.yaml",  # 零覆盖登记
    "tar czf " + CFG + " -C D:/myagent workspace",         # 登记: 半匹配边界
    "ln -sf " + CFG + " " + WS,                            # 登记
])
print("--- env var red line sanity ---")
print("HERMES_HOME =", os.environ.get("HERMES_HOME"), "| _hermes_home() =", h._hermes_home())
