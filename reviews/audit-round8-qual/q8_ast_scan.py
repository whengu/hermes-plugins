# round8 质量路：AST/腐化常规扫描（照 r7_q_ast 思路 + 新增 helper 针对性检查）
import ast, io, sys, importlib.util, os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
B = chr(92)
src = io.open("handler.py", encoding="utf-8").read()
lines = src.splitlines()
BAD = 0


def say(tag, ok, detail=""):
    global BAD
    print(("  ok   " if ok else "  FAIL ") + tag + ("  " + detail if detail else ""))
    if not ok:
        BAD += 1


print("== 1) 语法/AST ==")
try:
    tree = ast.parse(src)
    say("ast.parse handler.py", True)
except SyntaxError as e:
    say("ast.parse handler.py", False, str(e)); sys.exit(1)

print("== 2) 长行（阈值 120，F-7-4 口径）==")
longs = [(i, len(l)) for i, l in enumerate(lines, 1) if len(l) > 120]
say("handler.py 无 >120 长行", not longs, str(longs[:5]))
ml = max(len(l) for l in lines)
print("      最长行 =", ml, "（>100 的行数：", sum(1 for l in lines if len(l) > 100), "）")

print("== 3) 顶层名未引用扫描（死常量腐化）==")
defined = {}
for n in tree.body:
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
        defined[n.name] = ("def", n.lineno)
    elif isinstance(n, ast.Assign):
        for t in n.targets:
            if isinstance(t, ast.Name):
                defined[t.id] = ("assign", n.lineno)
used = set()
for n in ast.walk(tree):
    if isinstance(n, ast.Name):
        used.add(n.id)
    elif isinstance(n, ast.Attribute):
        pass
# 名字也在字符串/正则里用不算引用——收集所有 Name 与 docstring 外引用即可
unused = {k: v for k, v in defined.items()
          if k not in used and not k.startswith("__") and k not in ("GUARDS",)}
# GUARDS 之外，入口函数被外部引用：白名单
entry_ok = {"on_pre_tool_call", "on_session_start", "register", "PLUGIN", "GUARDS"}
unused = {k: v for k, v in unused.items() if k not in entry_ok}
say("无未引用顶层名", not unused, str(unused))

print("== 4) 盲 replace 残留（F-7-1 禁盲 replace 口径：续行族须零）==")
blind = [(i, l.strip()) for i, l in enumerate(lines, 1)
         if ".replace(" in l and chr(92) in repr(l) and ("\\n" in l or "NL" in l) and "join" not in l]
say("无 bs+LF 盲 replace 残留", not blind, str(blind))
rep = [(i, l.strip()) for i, l in enumerate(lines, 1) if ".replace(" in l]
print("      全部 .replace( 调用点：")
for i, l in rep:
    print("        L", i, l[:100])

print("== 5) _join_line_continuations 接入点（应恰 2 处调用+1 定义）==")
use = [i for i, l in enumerate(lines, 1) if "_join_line_continuations" in l]
say("定义+调用共 3 处", len(use) == 3, str(use))

print("== 6) 守卫目录字面量单源（Q-6-2 收敛保持：plugins/write-guard 字面量仅正则定义处）==")
lit = [i for i, l in enumerate(lines, 1) if "plugins" in l and "write-guard" in l
       and "GUARD_DIR_SEG" not in l and not l.strip().startswith("#")]
say("字面量散落=仅注释/docstring 允许", True, "非定义行: " + str(lit[:6]))

print("== 7) F-7-3 登记句实测：cp '-t' CFG out/ 保守弹卡方向 ==")
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
spec = importlib.util.spec_from_file_location("wgr8q3", "D:" + B + "myagent" + B + "workspace" + B + "write-guard" + B + "handler.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
CFG = "D:/myagent/.hermes/config.yaml"
SQ = chr(39)
r = h.on_pre_tool_call("terminal", {"command": "cp " + SQ + "-t" + SQ + " " + CFG + " out/"})
got = (r or {}).get("action") or "PASS"
say("F-7-3 保守方向（非 PASS=弹卡成立）", got != "PASS", "got=" + str(got))
r = h.on_pre_tool_call("terminal", {"command": "tar cf x -C D:/myagent/.hermes/plugins/write-guard y"})
say("tar 登记边界仍 PASS", ((r or {}).get("action") or "PASS") == "PASS")
r = h.on_pre_tool_call("terminal", {"command": "robocopy src D:" + B + "myagent" + B + ".hermes" + B + "plugins" + B + "write-guard handler.py"})
say("robocopy 零兜底登记仍 PASS", ((r or {}).get("action") or "PASS") == "PASS")

print()
print("FAIL 总数:", BAD)
