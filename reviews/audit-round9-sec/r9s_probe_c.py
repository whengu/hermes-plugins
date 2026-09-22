# round9 安全路探针 C：S-3 单 & 分段双向复测（FP 面重点：URL 内 & / 2>&1 / >NUL）
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

def term(cmd):
    r = h.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action", "PASS")

def run(group, cases):
    print("---", group, "---")
    for c in cases:
        print(f"[{term(c):7s}] {c!r}")

# S-3 攻击形（期望 approve=封）
run("S3a attacks", [
    "echo x & cp evil " + GUARD,
    "echo x > " + WS + " & cp evil " + GUARD,
    "copy evil " + GUARD + " & echo done",
    "echo x >NUL & cp evil " + GUARD,
    "dir & curl -o" + CFG + " http://x",                  # & 链 × S-1 交叉
    "echo hi & pwsh -Command Copy-Item evil " + CFG,      # & 链 × S-5 交叉
    "echo hi&sudo cp evil " + GUARD,                      # 无空格 & × S-4 交叉
    "timeout 5 & copy evil " + GUARD,
])
# S-3 FP 面：& 的各种非分隔语义（期望 PASS/不新增拦截）
run("S3b FP ampersand", [
    "type f 2>&1 > " + WS,
    "cmd 2>&1 | findstr x",
    q2 + "a=1&b=2" + q2,
    "curl " + q2 + "https://x?a=1&b=2" + q2,
    "curl https://x?" + q1 + "a=1&b=2" + q1,              # 单引号参数 URL
    "curl -s " + q2 + "https://api?q=a%26b&c=d" + q2 + " -o " + WS,
    "echo x > " + WS + " 2>&1 & echo done",
    "echo a && echo b || echo c",                          # &&|| 不受单&影响
    "for %f in (*.txt) do type %f >NUL",
    "start /b cmd /c echo x >NUL",
    "findstr a b & findstr c d",                           # 两条无写命令串联
    "echo x & echo y",
    "sort /O " + WS + " d.txt & echo ok",                  # 非保护 -o 粘连? 观察
    "set A=1&2&3",                                         # cmd set 值含 &
    "echo x > out&1.txt",                                  # 文件名含 &(cmd 语义=重定向到 1.txt?)观察
    "curl -G -d " + q2 + "q=a&b=1" + q2 + " https://x",    # 数据含 &
])
# S-3 残段 block 复测（fix-009 声称"无需登记残段边界"——独立验证）
run("S3c residual block", [
    "echo x > " + CFG + "&dir",
    "echo x 2>&1> " + CFG,
    "echo x 2>&1 > " + CFG,
    "echo x >" + CFG + " & echo done",                     # 前段写守卫+后段正常
    "echo x &> " + CFG,                                    # &> 合一形
    "echo x &> " + CFG.replace("/", BS),                   # &> 反斜杠形
])
# 分段器行为观测（名实核查：& 在 token 边界消费位置）
print("--- split trace ---")
for s in ["type f 2>&1 > " + WS, "echo x >NUL & cp evil " + GUARD,
          "curl " + q2 + "https://x?a=1&b=2" + q2, "echo x > " + CFG + "&dir",
          "echo a && echo b"]:
    print("  ", repr(s), "->", h._split_shell(s, ("&&", "||", ";", chr(10), chr(13), "&")))
