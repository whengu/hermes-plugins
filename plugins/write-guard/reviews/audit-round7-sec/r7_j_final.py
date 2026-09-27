# -*- coding: utf-8 -*-
"""J 卷终测：half1/引号粘连形 对准 GUARD 的守卫判定终值（shell 真值已在 I 卷证）。
J1 cp -'t'<GUARD> evil / cp -"t"<GUARD> evil      （shell= -t 生效,预判守卫 PASS=旁路）
J2 cp '-t'<GUARD> evil（预判 QUOTED search(before) 命中=拦）
J3 POSIX 平台差异形：ls \\<LF>truncate CFG 守卫粘连视图→PASS?（F-R7-8 佐证）
J4 引号选项后置形 cp evil '-t'<GUARD>（-t 目标合法在任意位）
J5 cp evil -'t'<GUARD>
"""
import importlib.util, os
os.environ["HERMES_HOME"] = r"D:\myagent\.hermes"
os.chdir(r"D:\myagent\workspace")
spec = importlib.util.spec_from_file_location("wg7j", r"D:\myagent\workspace\write-guard\handler.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
NL, CR, B, Q1, Q2 = chr(10), chr(13), chr(92), chr(39), chr(34)
HOME = "D:/myagent/.hermes"
GUARD = HOME + "/plugins/write-guard"
CFG = HOME + "/config.yaml"
def act(c):
    r = h.on_pre_tool_call("terminal", {"command": c})
    return (r or {}).get("action") or "PASS"
print("J1a cp -'t'GUARD evil        ->", act("cp -" + Q1 + "t" + Q1 + GUARD + " evil"), "(PASS=旁路实锤)")
print("J1b cp -\"t\"GUARD evil        ->", act("cp -" + Q2 + "t" + Q2 + GUARD + " evil"), "(PASS=旁路实锤)")
print("J2  cp '-t'GUARD evil         ->", act("cp " + Q1 + "-t" + Q1 + GUARD + " evil"), "(预期approve=已封)")
print("J3  ls a \\\\<LF>truncate CFG ->", act("ls a " + B*2 + NL + "truncate -s 0 " + CFG), "(POSIX真值SPLIT时=旁路;本机MSYS JOIN)")
print("J4  cp evil '-t'GUARD         ->", act("cp evil " + Q1 + "-t" + Q1 + GUARD), "(预期approve)")
print("J5  cp evil -'t'GUARD         ->", act("cp evil -" + Q1 + "t" + Q1 + GUARD), "(PASS=旁路)")
print("J6  install -'t'HOME x        ->", act("install -" + Q1 + "t" + Q1 + HOME + " x"), "(PASS=旁路)")
print("J7  cp -'t' sub 负例(非保护)   ->", act("cp -" + Q1 + "t" + Q1 + "D:/myagent/workspace/sub x"), "(PASS=正确)")
print("J8  cp '-t' -- 干扰: cp '-T'GUARD (大写T GNU不同义) ->", act("cp " + Q1 + "-T" + Q1 + GUARD + " evil"), "(PASS=设计如此)")
print("J9  token 视图自检: ")
seg = "cp -" + Q1 + "t" + Q1 + GUARD + " evil"
print("    tokens:", [m.group(0)[:24] for m in h._PATH_TOKEN_RE.finditer(seg)])
