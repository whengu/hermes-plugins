# round9 安全路探针 H：补充精查（tee 多目标 / copy /Y / .exe 与绝对路径命令词两代际 /
# wrapper×embed×S-1 三重交叉 / S-3 额外 FP 形 / S-2 修法可行性面）
import importlib.util, os
BS = chr(92)
os.environ["HERMES_HOME"] = "D:" + BS + "myagent" + BS + ".hermes"
os.chdir("D:" + BS + "myagent" + BS + "workspace")
HERE = os.path.dirname(os.path.abspath(__file__))
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
ho = load("ho", os.path.join(HERE, "scratch", "handler_old.py"))
h = load("h", os.path.join(HERE, "..", "..", "handler.py"))
CFG = "D:/myagent/.hermes/config.yaml"
GUARD = "D:/myagent/.hermes/plugins/write-guard"
HD = GUARD + "/handler.py"
WS = "D:/myagent/workspace/a.txt"
q1, q2 = chr(39), chr(34)

def act(mod, c, tool="terminal"):
    arg = "command" if tool == "terminal" else "code"
    r = mod.on_pre_tool_call(tool, {arg: c})
    return (r or {}).get("action", "PASS")

def run(group, cases):
    print("---", group, "---")
    for c in cases:
        print(f"old={act(ho,c):7s} new={act(h,c):7s}  {c!r}")

run("H1 tee 多目标/位参", [
    "echo x | tee evil.txt " + CFG,                 # 非首位 tee 目标
    "tee " + CFG + " out2.txt",                      # tee 首位但非末位
    "echo x | tee -a evil.txt " + CFG,
    "echo x | tee " + CFG,                           # 基准 block
    "echo x | tee " + WS,                            # 负例
])
run("H2 copy 开关/绝对路径/.exe", [
    "copy /Y evil " + CFG,
    "copy /y " + WS + " " + CFG,
    "cp.exe evil " + GUARD,
    "copy.exe evil " + GUARD,
    "/usr/bin/cp evil " + GUARD,
    "D:" + BS + "tools" + BS + "cp.exe evil " + GUARD,
    "cp.exe evil " + CFG,
    "/bin/cp evil " + CFG,
    "sed.exe -i s/a/b/ " + CFG,                      # 对照：sed .exe 命中
    "curl.exe -o " + CFG + " http://x",
])
run("H3 wrapper × embed × S-1", [
    "sudo bash -c " + q2 + "curl -o" + CFG + " http://x" + q2,
    "sudo bash -c " + q2 + "echo x > " + CFG + q2,
    "sudo cmd /c copy evil " + CFG,
    "sudo sh -c cp evil " + GUARD,
    "nohup bash -c " + q2 + "cp evil " + GUARD + q2,
    "time bash -c " + q2 + "echo x > " + CFG + q2,
])
run("H4 S-3 额外 FP 面", [
    "type f 2>&1 >NUL",
    "echo x >NUL 2>&1",
    "dir >NUL & dir >NUL",
    "find /i x y & sort " + CFG + " > " + WS,        # 守卫作源、ws 作目标
    "ping -n 1 host & echo done",
    "echo a&echo b&cp " + CFG + " " + WS,            # 三段：仅源位 cp 应 PASS
    "curl -s https://x -o out.bin & type f 2>&1",
    "echo x 1>&2",
    "echo x >&2",
])
run("H5 S-2 位参修法可行性观察（哪些分支命中）", [
    "pwsh -Command " + q2 + "Copy-Item " + CFG + " " + WS + q2,     # 源位=应 PASS
    "pwsh -Command " + q2 + "Copy-Item " + WS + " " + CFG + q2,     # 目标=应拦向
    "Copy-Item -Path " + WS + " -Destination " + CFG,               # 目标=应拦向
    "Copy-Item -Container " + CFG + " -Destination " + WS,          # -Path 缺位源
    "Copy-Item " + CFG + " -Destination " + WS,                      # 命名目标位源
])
print("--- token 视图（矩阵前判定位参可行性）---")
for s in ["Copy-Item " + CFG + " " + WS, "Copy-Item " + WS + " " + CFG]:
    segs = h._split_shell(s, ("&&", "||", ";", chr(10), chr(13), "&"))
    print(" ", repr(s), "cw=", h._command_word(s))
    for m in h._PATH_TOKEN_RE.finditer(segs[0]):
        raw = m.group(0)
        print("    tok", repr(raw), "->", h._normalize_path(raw),
              "write?", h._terminal_position_is_write(segs[0], m, raw,
                                                     h._normalize_path(raw), os.getcwd()))
print("--- PS 正则视图 ---")
for s in ["Copy-Item a b", "Tee-Object a b", "cp a b", "tee a b"]:
    print("  ", repr(s), "PS_WRITE:", bool(h._PS_WRITE_RE.search(s)))
