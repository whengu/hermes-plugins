# round8 质量路名实对读探针（载荷文件内构造，零命令行载荷）
import importlib.util, os

B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
spec = importlib.util.spec_from_file_location(
    "wgr8q", "D:" + B + "myagent" + B + "workspace" + B + "write-guard" + B + "handler.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)

NL, CR, SQ, DQ = chr(10), chr(13), chr(39), chr(34)
HOME = "D:/myagent/.hermes"
GUARD = HOME + "/plugins/write-guard"


def act(tool, args):
    r = h.on_pre_tool_call(tool, args)
    return (r or {}).get("action") or "PASS"


print("== 登记句对读：CHANGELOG『劈 token 穿插族(cp -'t'DIR / -\"t\"DIR) PASS』 ==")
print("cp -'t'GUARD evil   ->", act("terminal", {"command": "cp -" + SQ + "t" + SQ + GUARD + " evil"}))
print('cp -"t"GUARD evil   ->', act("terminal", {"command": "cp -" + DQ + "t" + DQ + GUARD + " evil"}))
print("install -'t'HOME x  ->", act("terminal", {"command": "install -" + SQ + "t" + SQ + HOME + " x"}))
print('install -"t"HOME x  ->', act("terminal", {"command": "install -" + DQ + "t" + DQ + HOME + " x"}))
print("对照 cp '-t'GUARD x ->", act("terminal", {"command": "cp " + SQ + "-t" + SQ + GUARD + " x"}))

print("== 登记句对读：『反斜杠逐对消耗自然满足奇偶语义』 vs fix-008-input §1b『奇数末位粘连』 ==")
for k in (2, 3, 4, 5, 6, 7):
    src = "cp evil " + B * k + NL + GUARD
    joined = h._join_line_continuations(src)
    print(f"{k}bs+LF: join后含LF={'LF残留' if NL in joined else '粘连'} -> 判定",
          act("terminal", {"command": src}))

print("== 其余抽查：双引号内续行 / 转义对不被吞 ==")
print('echo "a\\LF+GUARD" ->', act("terminal", {"command": "echo " + DQ + "a" + B + NL + GUARD + DQ}))
print("cp evil \\LF GUARD ->", act("terminal", {"command": "cp evil " + B + NL + GUARD}))
print("2bs 分段旁路形    ->", act("terminal", {"command": "echo a" + B + B + NL + "cp evil " + GUARD}))
print("gateway \\CRLF restart ->", act("terminal", {"command": "hermes gateway " + B + CR + NL + "restart"}))
print('cp "-t" GUARD x (空格式) ->', act("terminal", {"command": "cp " + DQ + "-t" + DQ + " " + GUARD + " x"}))
print("负例 grep '-t' file ->", act("terminal", {"command": "grep " + SQ + "-t" + SQ + " somefile.txt"}))
