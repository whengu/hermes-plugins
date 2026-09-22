# round12 安全路探针 D：红线四形 + 处置分流 + 引号粘连变体 + 部署一致性
import importlib.util, os
BS, q1, q2 = chr(92), chr(39), chr(34)
os.environ["HERMES_HOME"] = "D:" + BS + "myagent" + BS + ".hermes"
os.chdir("D:" + BS + "myagent" + BS + "workspace")
HERE = os.path.dirname(os.path.abspath(__file__))

def load(tag, path):
    spec = importlib.util.spec_from_file_location(tag, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

new = load("hn", os.path.join(HERE, "..", "..", "handler.py"))
r11 = load("h11", os.path.join(HERE, "..", "..", "_r2tmp", "handler_r11_94998f5.py"))
HOME = "D:/myagent/.hermes"
CFG = HOME + "/config.yaml"
GSRC = HOME + "/plugins/write-guard/handler.py"
WS = "D:/myagent/workspace/a.txt"

def act(mod, cmd):
    r = mod.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action") or "PASS"

print("--- 红线四形 ---")
RED = [
    ("R1 gateway restart block", "hermes gateway restart", "block"),
    ("R1b bs+LF 续行", "hermes gateway \\\nrestart", "block"),
    ("R1c sudo/&/引号载体交叉", 'sudo bash -c "hermes gateway restart"', "block"),
    ("R1d status 不误伤", "hermes gateway status", "PASS"),
    ("R2 cp 配置弹卡", "cp backup.yaml " + CFG, "approve"),
    ("R2b Copy-Item 目标配置弹卡", "Copy-Item x " + CFG, "approve"),
    ("R3 Copy-Item 源位 PASS", "Copy-Item " + CFG + " D:/ws/bak.yaml", "PASS"),
    ("R4 rm -r 分层不扩", "rm -rf " + HOME, "PASS"),
    ("R4b rd /s /q 分层", "rd /s /q D:\\myagent\\.hermes", "PASS"),
]
for tag, cmd, want in RED:
    got = act(new, cmd)
    print(("ok  " if got == want else "DIFF"), f"{tag:38s} got={got:8s} want={want}")
print("--- 处置分流 ---")
DIS = [
    ("冒号粘连写配置=approve 弹卡", "Copy-Item -Destination:" + CFG + " x", "approve"),
    ("curl -o 族写守卫源码=block", "curl -o " + GSRC + " http://x", "block"),
    ("curl 引号选项词写守卫源码=block", 'curl "-o" ' + GSRC + " http://x", "block"),
    ("cp 写守卫源码=approve(复制族弹卡)", "cp evil.py " + GSRC, "approve"),
]
for tag, cmd, want in DIS:
    got = act(new, cmd)
    print(("ok  " if got == want else "DIFF"), f"{tag:38s} got={got:8s} want={want}  {cmd!r}")
print("--- 引号粘连/cluster 变体（三代） ---")
VAR = [
    ('v1 curl "-o<CFG>" 双引包粘连', "curl " + q2 + "-o" + CFG + q2 + " http://x"),
    ("v2 curl '-o<CFG>' 单引包粘连", "curl " + q1 + "-o" + CFG + q1 + " http://x"),
    ('v3 curl "-so<CFG>" cluster引号粘连', "curl " + q2 + "-so" + CFG + q2 + " http://x"),
    ('v4 curl "-so" CFG cluster整词引号+空格值', "curl " + q2 + "-so" + q2 + " " + CFG + " http://x"),
    ('v5 curl "--output=<CFG>" 引号包等号', "curl " + q2 + "--output=" + CFG + q2 + " http://x"),
    ('v6 wget "-O<CFG>" 大写粘连(远端名语义)', "wget " + q2 + "-O" + CFG + q2 + " http://x"),
    ('v7 NEG curl "-o" 非保护', "curl " + q2 + "-o" + q2 + " D:/ws/x.txt http://x"),
    ('v8 NEG echo "-o<CFG>" 门外文本', 'grep "-o" ' + CFG),
    ("v9 cluster -sSO 大写尾O(远端名)", "curl -sSO " + CFG),
    ("v10 curl -fo CFG(-f+-o 真写)", "curl -fo " + CFG + " http://x"),
]
for tag, cmd in VAR:
    print(f"  new={act(new,cmd):8s} r11={act(r11,cmd):8s} | {tag} :: {cmd!r}")
