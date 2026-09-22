# round11 安全路探针 C：跨代际逐形漂移 diff（r10=2cc28cf 快照 vs r11=现行 handler）
# 形集=round10 探针 a~h 全部实跑命令（从其 stdout 的 repr 解析）+ 本轮关键补充形。
# 判读基准：r10 -era 的 got（探针输出第三列）= 上一轮实测事实；r11 got 与之差异
# 只允许出现在 F-10-1/F-10-2 预期翻转面。预期外漂移=回归 finding。
import importlib.util, os, re, ast, subprocess
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
old = load("ho", os.path.join(HERE, "..", "audit-round10-qual", "base", "handler_r10commit.py"))

probes = ["r10s_probe_a_f91.py", "r10s_probe_b_f92.py", "r10s_probe_c_f93_f94.py",
          "r10s_probe_d_redlines_new.py", "r10s_probe_e_f93_neighbors.py",
          "r10s_probe_f_named_target_fp.py", "r10s_probe_g_named_target.py",
          "r10s_probe_h_evidence_fix.py"]
LINE = re.compile(r"^\[.{2,6}\] (\S+)\s+want=\S+\s+.*?:: (.*)$")
seen, cases = set(), []   # (cmd, r10_era_got)
for p in probes:
    out = subprocess.run(["python", os.path.join(HERE, "..", "audit-round10-sec", p)],
                         capture_output=True, text=True, errors="replace").stdout
    n = 0
    for ln in out.splitlines():
        m = LINE.match(ln.strip())
        if not m:
            continue
        got, rep = m.group(1), m.group(2)
        try:
            cmd = ast.literal_eval(rep)
        except Exception:
            continue
        if isinstance(cmd, str) and cmd not in seen:
            seen.add(cmd); cases.append((cmd, got)); n += 1
    print(f"{p}: 收 {n} 形")

HOME = "D:/myagent/.hermes"
CFG = HOME + "/config.yaml"
WS = "D:/myagent/workspace/a.txt"
BAK = "D:/myagent/workspace/bak.yaml"
extra = [
    "Copy-Item -Destination " + CFG + " " + WS,
    "Copy-Item -Destination " + WS + " " + CFG,
    "Copy-Item -Container " + CFG + " -Destination " + BAK,
    "Copy-Item -Path " + CFG + " -Destination " + BAK,
    "Tee-Object -FilePath " + CFG + " -InputObject x",
    'pwsh -Command "Copy-Item -Destination ' + CFG + " " + WS + '"',
    "sort D:/myagent/workspace/o " + CFG,
    "sort D:/myagent/workspace/my-dir-o " + CFG,
    "curl -o " + CFG + " http://x",
    "curl -sSL -o" + CFG + " http://x",
    "Set-Content " + CFG + " x",
]
for c in extra:
    if c not in seen:
        seen.add(c); cases.append((c, "?r11-new-shape"))

def act(mod, cmd):
    r = mod.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action") or "PASS"

diff = []
for c, era in cases:
    a_old, a_new = act(old, c), act(new, c)
    if a_old != a_new:
        diff.append((c, a_old, a_new, era))
print(f"\n共比对 {len(cases)} 形；跨代漂移 {len(diff)} 形：")
for c, a, b, era in diff:
    print(f"  r10={a:8s}-> r11={b:8s} (r10探针记={era:8s}) :: {c!r}")
