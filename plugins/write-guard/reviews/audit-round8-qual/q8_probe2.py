# round8 质量路：补探针（fix-008 §0 声称的修后方向 + CHANGELOG 未锚定形）+ baseline 复测
import importlib.util, os, subprocess, pathlib

B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
spec = importlib.util.spec_from_file_location(
    "wgr8q2", "D:" + B + "myagent" + B + "workspace" + B + "write-guard" + B + "handler.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)

NL, CR, SQ, DQ = chr(10), chr(13), chr(39), chr(34)
GUARD = "D:/myagent/.hermes/plugins/write-guard"


def act(tool, args):
    r = h.on_pre_tool_call(tool, args)
    return (r or {}).get("action") or "PASS"


print("== 当前代码（a0dab67）==")
print("1) cp '-t'=GUARD x  (fix-008 §0 行23 声称修后 approve) ->",
      act("terminal", {"command": "cp " + SQ + "-t" + SQ + "=" + GUARD + " x"}))
print("2) cp -\"target-directory\" GUARD evil (boundary§排除1 列名形, shell真值= -t arget-directory 簇)")
print("   ->", act("terminal", {"command": "cp -" + DQ + "target-directory" + DQ + " " + GUARD + " evil"}))
print("3) cp -'target-directory'=GUARD x (半混 tdir= 候选1) ->",
      act("terminal", {"command": "cp -" + SQ + "target-directory" + SQ + "=" + GUARD + " x"}))
print("4) cp -\"--target-directory\"=GUARD x (半混 tdir= 候选2) ->",
      act("terminal", {"command": "cp -" + DQ + "--target-directory" + DQ + "=" + GUARD + " x"}))
print("5) cp '-t'-GUARD x ('-t'- 逐字符拆引号族代表) ->",
      act("terminal", {"command": "cp " + SQ + "-t" + SQ + "-" + GUARD + " x"}))
print("6) CP EVIL \\\\LF GUARD 大写命令词+续行 ->",
      act("terminal", {"command": "CP evil " + B + NL + GUARD}))

print("== baseline 90de321（fix-008 §0 行1 声称修前=approve；fix-008-input 声称修前=PASS）==")
base_path = pathlib.Path(r"D:/myagent/workspace/write-guard/reviews/audit-round8-qual/_q8_base90de321.py")
base_path.write_bytes(subprocess.run("git show 90de321:handler.py", shell=True,
                                     capture_output=True).stdout)
spec2 = importlib.util.spec_from_file_location("wgr8base", str(base_path))
h2 = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(h2)


def act2(tool, args):
    r = h2.on_pre_tool_call(tool, args)
    return (r or {}).get("action") or "PASS"


print("b1) cp evil \\\\LF GUARD (真续行) ->", act2("terminal", {"command": "cp evil " + B + NL + GUARD}))
print("b2) echo a + 2bs + LF + cp evil GUARD ->",
      act2("terminal", {"command": "echo a" + B + B + NL + "cp evil " + GUARD}))
print("b3) gateway bs+CRLF restart ->", act2("terminal", {"command": "hermes gateway " + B + CR + NL + "restart"}))
print("b4) cp \"--target-directory\"=GUARD x ->",
      act2("terminal", {"command": "cp " + DQ + "--target-directory" + DQ + "=" + GUARD + " x"}))
print("b5) cp -\"--target-directory\" GUARD evil 半混(整词) ->",
      act2("terminal", {"command": "cp -" + DQ + "--target-directory" + DQ + " " + GUARD + " evil"}))
print("b6) cp \"target\" 读整词引号 cat ->", act2("terminal", {"command": "cat " + SQ + GUARD + "/handler.py" + SQ}))
