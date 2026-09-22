# round12 安全路探针 C v2：round11 探针全集回归 + 代际差分
# 形集 = 执行 r11s_probe_a/b/e 源码 + r11s_rerun_*.out + pm_verify_012/011 表 + test_handler
# _call("terminal",{...}) 字面量，harvest repr 命令行；逐形 new(4e254c8) vs r11(94998f5) 实跑。
import importlib.util, os, re, ast, subprocess, glob, sys
BS = chr(92)
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

def act(mod, cmd):
    r = mod.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action") or "PASS"

LINE = re.compile(r":: (.*)$")
seen, cmds = set(), []
def harvest(text):
    for ln in text.splitlines():
        m = LINE.search(ln)
        if not m:
            continue
        try:
            cmd = ast.literal_eval(m.group(1).strip())
        except Exception:
            continue
        if isinstance(cmd, str) and cmd and cmd not in seen:
            seen.add(cmd); cmds.append(cmd)

# 1) 执行 round11 探针 a/b/e（其 stdout 即 r11-era 实测形集全集，含全部 lock 面）
for p in ["r11s_probe_a_fix_retest.py", "r11s_probe_b_bypass_fp.py", "r11s_probe_e_newfaces.py"]:
    fp = os.path.join(HERE, "..", "audit-round11-sec", p)
    try:
        out = subprocess.run([sys.executable, fp], capture_output=True, text=True,
                             errors="replace", timeout=180).stdout
        harvest(out)
    except Exception as e:
        print("PROBE RUN FAIL", p, e)
# 2) rerun 日志 + PM 基线日志（pm012 表行）
for pat in ["../audit-round11-sec/r11s_rerun_*.out", "../../_r2tmp/wg_r12s_base.log"]:
    for f in glob.glob(os.path.join(HERE, pat)):
        harvest(open(f, encoding="utf-8", errors="replace").read())
# 3) pm_verify 源码内联字面量（拼接式：exec 提取其 cases）
TC = re.compile(r"\"command\": (\".*?\")")
th = open(os.path.join(HERE, "..", "..", "test_handler.py"), encoding="utf-8").read()
for m in re.finditer(r"_call\(\"terminal\", \{\"command\": (\".*?\"|'.*?')\}\)", th):
    try:
        c = ast.literal_eval(m.group(1))
        if c not in seen:
            seen.add(c); cmds.append(c)
    except Exception:
        pass
# 4) round12 探针 a/b 自 harvest（新邻域形也进代际面）
for f in ["r12s_probe_a_fix_retest.py", "r12s_probe_b_bypass_fp.py"]:
    fp = os.path.join(HERE, f)
    if os.path.exists(fp):
        out = subprocess.run([sys.executable, fp], capture_output=True, text=True,
                             errors="replace", timeout=240).stdout
        harvest(out)

FLIP_HINT = re.compile(r"-Destination:|-FilePath:|\"-o\"|'-o'|\"--output|\"-O\"|\"--output"
                       r"| -so | -sSLfo | -qO | -ro | -o\"|\"-o"
                       r"|Copy-Item -Path |Copy-Item -Destination \S+ -Path|Copy-Item -Destination \S+ -LiteralPath")
print("harvest 形数:", len(cmds))
print("--- 代际差异行（r11→new）---")
nd = 0
for c in cmds:
    g, o = act(new, c), act(r11, c)
    if g != o:
        nd += 1
        hint = " [∈预期翻转族]" if FLIP_HINT.search(c) else " [!! 预期外]"
        print(f"  {o:8s} -> {g:8s}{hint} :: {c!r}")
print("差异总数:", nd)
# 全集双向统计（供报告）
nb = sum(1 for c in cmds if act(new, c) != "PASS")
print(f"new 命中(非PASS)形数: {nb} / {len(cmds)}")
