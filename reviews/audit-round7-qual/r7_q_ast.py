# round7 质量复审：AST 腐化扫描 + 边界登记核对 + 部署一致性（只读）
import ast, io, subprocess, sys, os

def run(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return (p.stdout or "") + (p.stderr or "")

print("== 1) 长行扫描（>100 字符）==")
src = io.open("handler.py", encoding="utf-8").read()
longs = [(i, len(l)) for i, l in enumerate(src.splitlines(), 1) if len(l) > 100]
print(longs if longs else "无 >100 字符行（Q-6-3 名实相符）")
print("== 2) AST 可解析 + 死支粗扫（函数体内恒不可达分支 not in _is_guard_dir_target）==")
tree = ast.parse(src)
fn = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_is_guard_dir_target"][0]
print("return 语句数:", sum(1 for n in ast.walk(fn) if isinstance(n, ast.Return)))
print("『guard_dir』字面量残留次数:", src.count("guard_dir ="))
print("『write-guard』字符串拼接残留（除正则与注释外）:", [i for i, l in enumerate(src.splitlines(), 1) if ('"plugins" +' in l)])
print("== 3) _is_guard_dir_target 调用点（冗余条件观察）==")
for i, l in enumerate(src.splitlines(), 1):
    if "_is_guard_dir_target(" in l and "def " not in l and "#" not in l[:4]:
        print("USE", i, l.strip())
print("== 4) 部署一致性：git 基线 vs 主部署 vs 镜像 ==")
base = run('git show 90de321:handler.py > .r7_base_handler.tmp')
b = io.open(".r7_base_handler.tmp", "rb").read()
for tag, p in [("main", r"D:/myagent/.hermes/plugins/write-guard/handler.py"),
               ("mirror-arch", r"D:/myagent/.hermes/profiles/architect/plugins/write-guard/handler.py"),
               ("mirror-dev", r"D:/myagent/.hermes/profiles/developer/plugins/write-guard/handler.py")]:
    try:
        same = io.open(p, "rb").read() == b
        print(tag, "IDENTICAL" if same else "DIFFERS!")
    except FileNotFoundError:
        print(tag, "MISSING", p)
os.remove(".r7_base_handler.tmp")
print("== 5) CHANGELOG 关键登记断言实测 ==")
# 已登记不修面抽查：robocopy 零兜底、spawn-exec、tar/ln
import importlib.util
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
spec = importlib.util.spec_from_file_location("wgq2", "handler.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
CFG = "D:/myagent/.hermes/config.yaml"; GUARD = "D:/myagent/.hermes/plugins/write-guard"
def act(tool, args):
    r = h.on_pre_tool_call(tool, args)
    return (r or {}).get("action") or "PASS"
print("robocopy 三参写守卫目录（登记零兜底，期望 PASS=登记真实）:", act("terminal", {"command": "robocopy src " + GUARD.replace("/", B) + " handler.py"}))
print("tar -C 写（登记边界，期望 PASS）:", act("terminal", {"command": "tar cf x -C " + GUARD + " y"}))
print("os.spawnv argv（登记边界，期望 PASS）:", act("execute_code", {"code": "import os\nos.spawnv(os.P_WAIT, 'cp', ['cp', 'a', r'" + GUARD.replace("/", B) + "'])"}))
print("双反斜杠续行旁路（round7 新 finding 复测）:", act("terminal", {"command": "echo a" + B + B + chr(10) + "cp evil " + GUARD}))
print("== 6) requirement 边界条目 vs 实测：Q-6-1 注释宣称『与 getopt 语义一致』抽查 ==")
# getopt 语义：-tstage = -s -t age → 目标 cwd/age。守卫视角把整串 stage 当目标。
print("cd 非home && cp -tGUARDinside（若真 shell 目标=age 末段）:", act("terminal", {"command": "cd D:/tmpnote && cp -t" + GUARD + " x"}))
