# round9 安全路探针 B：S-2 cmdlet 扩集复测 + S-4 wrapper 剔除影响面（词提取 FP/漏双查）
import importlib.util, os
os.environ["HERMES_HOME"] = "D:" + chr(92) + "myagent" + chr(92) + ".hermes"
os.chdir("D:" + chr(92) + "myagent" + chr(92) + "workspace")
HG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "handler.py")
spec = importlib.util.spec_from_file_location("hg", HG)
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
BS, q1, q2 = chr(92), chr(39), chr(34)
HOME = "D:/myagent/.hermes"
CFG = HOME + "/config.yaml"
GUARD = HOME + "/plugins/write-guard"
HD = GUARD + "/handler.py"
WS = "D:/myagent/workspace/a.txt"
BAK = "D:/myagent/workspace/config.bak.yaml"

def term(cmd):
    r = h.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action", "PASS")

def run(group, cases):
    print("---", group, "---")
    for c in cases:
        print(f"[{term(c):7s}] {c!r}")

# S-2 攻击形
run("S2a attacks", [
    "pwsh -Command " + q2 + "Copy-Item evil " + CFG + q2,
    "pwsh -Command " + q2 + "Tee-Object -FilePath " + CFG + q2,
    "pwsh -Command Copy-Item evil " + CFG,                 # 裸形(联动 S-5)
    "Copy-Item evil " + CFG,                               # 载体外裸 cmdlet
    "Copy-Item -Path evil -Destination " + CFG,
    "pwsh -Command " + q2 + "Copy-Item evil " + GUARD + q2,  # 目标=守卫目录
    "pwsh -NoProfile -Command " + q2 + "Tee-Object -FilePath " + HD + q2,
])
# S-2 FP 面：受保护路径处于**源位**（读取/备份语义，对齐"改名/复制不拦"红线）
run("S2b source-position FP", [
    "Copy-Item " + CFG + " " + BAK,                        # 备份读源位
    "pwsh -Command " + q2 + "Copy-Item " + CFG + " " + BAK + q2,
    "pwsh -Command " + q2 + "Copy-Item " + HD + " out.py" + q2,
    "Copy-Item -Path " + CFG + " -Destination " + BAK,     # 源位显式命名
    "Tee-Object -InputObject x -FilePath " + WS,           # 非保护目标
    # 对照：cp 源位（既有正确行为）
    "cp " + CFG + " " + BAK,
])
# S-4 攻击形（wrapper × 写族 × 门族）
run("S4a attacks", [
    "sudo cp evil " + GUARD,
    "runas /user:admin cp evil " + GUARD,
    "LANG=C cp evil " + GUARD,
    "nohup cp evil " + GUARD + " &",
    "time cp evil " + GUARD,
    "env FOO=1 cp evil " + GUARD,
    "sudo install -t " + GUARD + " evil",
    "sudo tee " + CFG,
    "sudo sed -i s/a/b/ " + CFG,
    "sudo truncate -s 0 " + CFG,
    "env -i sudo -n time cp evil " + GUARD,               # 多 wrapper 叠罗汉 观察
    "sudo curl -o" + CFG + " http://x",                    # wrapper×S-1 交叉
    "sudo cmd /c copy evil " + CFG,                        # wrapper×S-5 交叉
])
# S-4 FP 面：剔除链对正常命令词提取的影响（读/常规写 workspace/无守卫词）
run("S4b FP surface", [
    "env | grep config",
    "time ls D:/myagent/workspace",
    "sudo cat " + HD,
    "nohup python server.py &",
    "sudo systemctl status nginx",
    "env PATH=/usr/bin cp note.txt " + WS,                 # 赋值+选项+正常写
    "time -p cp note.txt " + WS,
    "sudo rm note.txt",                                    # rm 属平台层, 插件应 PASS
    "runas /savecred /user:admin whoami",
    "sudo -u root cp evil " + GUARD,                       # 登记边界形: 期望 PASS(不立项)
    "env -u VAR cp evil " + GUARD,                         # env -u 带值形 观察
    "nice -n 5 cp evil " + GUARD,                          # 非名单 wrapper+带值 观察
    "xargs cp evil " + GUARD,                              # 非 wrapper 命令词
])
# S-4 词提取直接观测（名实核查: _command_word 前后对照面）
print("--- cw probes ---")
for s in ["sudo cp a b", "LANG=C cp a b", "runas /user:x cp a b", "nohup cp a b &",
          "env FOO=1 cp a b", "env | grep config", "sudo -u root cp a b",
          "/usr/bin/cp a b", "D:/tools/cp a b", "time -p cp a b",
          "-x cp a b", "install -t DIR evil", "sudo cmd /c copy a b"]:
    print(f"  cw({s!r}) = {h._command_word(s)!r}")
