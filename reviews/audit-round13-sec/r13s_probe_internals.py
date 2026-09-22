# r13 内部探针：H4 收集/判定链定位 + J 组复跑
import importlib.util, os
os.environ["HERMES_HOME"] = r"D:\myagent\.hermes"
os.chdir(r"D:\myagent\workspace")
spec = importlib.util.spec_from_file_location("wg", r"D:\myagent\workspace\write-guard\handler.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
def act(cmd):
    r = h.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action") or "PASS"
HOME = "D:/myagent/.hermes"; CFG = HOME + "/config.yaml"; W = "D:/myagent/workspace"
GUARD = HOME + "/plugins/write-guard"
print("hermes_home repr:", repr(h._hermes_home()), "SEP:", repr(h._SEP))
print("norm(guard fwd):", repr(h._normalize_path(GUARD, base=W)))
print("norm(guard slash):", repr(h._normalize_path(GUARD + "/", base=W)))
print("guard_dir_target:", h._is_guard_dir_target(h._normalize_path(GUARD, base=W)))
print("prot_cfg(norm of=CFG raw):", repr(h._normalize_path('"of=' + CFG + '"', base=W)))
seg = "cp '-t' " + GUARD + " evil.txt"
import re
for m in h._PATH_TOKEN_RE.finditer(seg):
    raw = m.group(0)
    n = h._normalize_path(raw, base=W)
    print("tok", repr(raw), "-> norm", repr(n))
# J 组复跑（上批输出疑似截断）
print("J1 wget \"-O<CFG>\":", act('wget "-O' + CFG + '" http://x'))
print("J2 wget \"-o<CFG>\":", act('wget "-o' + CFG + '" http://x'))
print("J3 wget -O" + CFG + " (bare glue ctrl):", act("wget -O" + CFG + " http://x"))
# H4 变体族：cp '-t' 引号选项词（需求纳入范围第3条例证同款）
print("K1 cp '-t' GUARD/ evil:", act("cp '-t' " + GUARD + "/ evil.txt"))
print("K2 cp \"-t\" GUARD/ evil:", act('cp "-t" ' + GUARD + '/ evil.txt'))
print("K3 cp '-t' CFG-dir evil (home root):", act("cp '-t' " + HOME + "/ evil.txt"))
print("K4 ctrl bare: cp -t GUARD/ evil:", act("cp -t " + GUARD + "/ evil.txt"))
print("K5 cp --target-directory GUARD/ evil (bare long):", act("cp --target-directory " + GUARD + "/ evil.txt"))
# dd of= 家族已证；补 tee 面引号值：echo x | tee \"CFG\"
print("L1 echo x|tee \\\"CFG\\\":", act('echo x | tee "' + CFG + '"'))
print("L2 sed -i \"CFG\"(quoted file):", act('sed -i s/a/b/ "' + CFG + '"'))
