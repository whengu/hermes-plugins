# round8 安全路探针 A：纳入范围常规形态（重定向/输出参数/内嵌一层/链式）
# 载荷全走常量拼接，避免命令行内联（round7 教训①）。
import importlib.util, os, sys

spec = importlib.util.spec_from_file_location("hg", sys.argv[1] if len(sys.argv) > 1 else "handler.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)

HOME = "D:/myagent/.hermes"          # == _hermes_home() 归一化值
BS = chr(92)
HOMEW = HOME.replace("/", BS)
CFG = HOME + "/config.yaml"
CFGW = HOMEW + BS + "config.yaml"
GUARD = HOME + "/plugins/write-guard"
HANDLER = GUARD + "/handler.py"
HANDLERW = GUARD.replace("/", BS) + BS + "handler.py"

def term(cmd):
    r = h.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action", "PASS")

def ec(code):
    r = h.on_pre_tool_call("execute_code", {"code": code})
    return (r or {}).get("action", "PASS")

def run(group, cases, judge=term):
    print(f"--- {group} ---")
    for cmd in cases:
        print(f"[{judge(cmd):7s}] {cmd!r}")


# §1 重定向族（常规人类写法全谱）
run("S1 redirect", [
    "echo x > " + CFG,
    "echo x >> " + CFG,
    "echo x >" + CFG,                    # 无空格粘连 >path
    "echo x >>" + CFG,
    "echo x > " + CFGW,                  # 反斜杠形
    "echo x >" + HANDLERW,               # 守卫源码本体
    "echo x 2>&1 > " + CFG,              # fd 复制+重定向常规组合
    "echo x > " + CFG + " 2>&1",
    "echo x | tee " + CFG,
    "echo x | tee -a " + CFG,
    "dd if=/dev/zero of=" + CFG,
    "sed -i s/a/b/ " + CFG,
    "sed -i 's/a/b/' " + CFG,
    "perl -pi -e s/a/b/ " + CFG,
])
# §1 输出参数族：带空格 vs 粘连（纳入范围第 4 条"常规选项粘连 -o<file>"）
run("S2 output-flag glue", [
    "curl -o " + CFG + " http://x",
    "curl -o" + CFG + " http://x",       # 粘连：范围文档§纳入4 点名词形
    "curl -O" + CFG + " http://x",
    "wget -o " + CFG + " http://x",
    "wget -o" + CFG + " http://x",
    "sort -o" + CFG + " d.txt",
    "curl --output" + CFG + " http://x", # 长选项无 = 粘连
])
# §3 整词引号包裹
q1, q2 = chr(39), chr(34)
run("S3 whole-token quotes", [
    "cp evil " + q1 + CFG + q1,
    "cp evil " + q2 + CFGW + q2,
    "cp " + q1 + "-t" + q1 + " " + HOME + " evil",
    "echo x > " + q1 + HANDLER + q1,
])
# §2 链式/管道/裸换行/真续行（F-7-1 修后面）
NL, CR = chr(10), chr(13)
run("S4 chain/newline/continuation", [
    "ls" + NL + "cp evil " + GUARD,
    "ls" + CR + NL + "cp evil " + GUARD,
    "ls; cp evil " + GUARD,
    "ls && cp evil " + GUARD,
    "ls || cp evil " + GUARD,
    "ls | cat; cp evil " + GUARD,
    "echo evil \\" + NL + GUARD + " x",              # cp evil \<LF>GUARD x
    "cp evil " + "\\" + NL + HANDLERW,               # 真续行粘连目标
    "cp evil " + "\\" + CR + NL + HANDLERW,          # bs+CRLF
])

