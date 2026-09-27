# round8 安全路探针 D：F-7-1/F-7-2 验收复测 + gateway 红线 + 排除形锁向
import importlib.util, os, sys
spec = importlib.util.spec_from_file_location("hg", "handler.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
CFG = "D:/myagent/.hermes/config.yaml"
GUARD = "D:/myagent/.hermes/plugins/write-guard"
HANDW = "D:\\myagent\\.hermes\\plugins\\write-guard\\handler.py"
NL, CR, bs, q1, q2 = chr(10), chr(13), chr(92), chr(39), chr(34)

def term(cmd):
    r = h.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action", "PASS")

def gw(cmd):
    r = h._guard_gateway_cmd("terminal", {"command": cmd}, "t")
    return (r or {}).get("action", "PASS")

def run(group, cases, judge=term):
    print("---", group, "---")
    for c in cases:
        print(f"[{judge(c):7s}] {c!r}")

# F-7-1 核心回归（应 approve / block）
run("R8-1 continuation", [
    "cp evil " + bs + NL + HANDW,
    "cp evil " + bs + CR + NL + HANDW,
    "echo a" + bs + bs + NL + "cp evil " + GUARD,
])
run("R8-1 accepted-locks", [
    "echo " + q2 + "a" + bs + NL + GUARD + q2,       # 双引号内续行：锁 PASS
    "echo " + q1 + "a" + bs + NL + q1 + " && cp evil " + GUARD,
    "echo a" + bs*3 + NL + "cp evil " + GUARD,        # 3bs 锁 approve
    "echo a" + bs*4 + NL + "cp evil " + GUARD,        # 4bs 锁 PASS
    "cp -" + q1 + "t" + q1 + GUARD + " evil",         # 劈token 锁 PASS
])
run("R8-2 tdir-quotted", [
    "cp " + q2 + "--target-directory" + q2 + "=" + GUARD + " evil",
    "cp " + q1 + "--target-directory" + q1 + "=" + GUARD + " evil",
    "cp " + q2 + "--target-directory" + q2 + "=" + "D:/myagent/workspace/sub" + " evil",  # 负例
])
run("gateway red line", [
    "hermes gateway " + bs + NL + "restart",
    "hermes gateway " + bs + CR + NL + "restart",
    "HERMES GATEWAY RESTART",
    "hermes -p dev gateway restart",
    "hermes gateway status",                          # 非禁动词 放行
], gw)
