# round8 质量路探针3：pre-r8 基线行为复测（直载 fix008-scratch/handler.pre-r8.py，
# 其行尾归一 sha 已验证 == git 90de321:handler.py），锚定 §0 修前声称与 round7 括注修正。
import importlib.util, os

B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
spec = importlib.util.spec_from_file_location(
    "wgr8base", "D:" + B + "myagent" + B + "workspace" + B + "write-guard"
    + B + "reviews" + B + "fix008-scratch" + B + "handler.pre-r8.py")
h2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h2)

NL, CR, SQ, DQ = chr(10), chr(13), chr(39), chr(34)
GUARD = "D:/myagent/.hermes/plugins/write-guard"
TD = "--target-directory"


def act2(tool, args):
    r = h2.on_pre_tool_call(tool, args)
    return (r or {}).get("action") or "PASS"


print("== pre-r8(=90de321) 基线行为（锚定 fix-008 §0 与 fix-008-input 冲突声称）==")
print("p1) cp evil bs+LF GUARD 真续行   [§0行13称approve / input称PASS] ->",
      act2("terminal", {"command": "cp evil " + B + NL + GUARD}))
print("p2) echo a 2bs LF cp evil GUARD   [§0行15称修前=旁路PASS]        ->",
      act2("terminal", {"command": "echo a" + B + B + NL + "cp evil " + GUARD}))
print("p3) gateway bs+CRLF restart       [括注称曾旁路]                 ->",
      act2("terminal", {"command": "hermes gateway " + B + CR + NL + "restart"}))
print("p4) gateway bs+LF restart         [修前已覆盖, 期望block]         ->",
      act2("terminal", {"command": "hermes gateway " + B + NL + "restart"}))
print("p5) cp dq tdir dq = GUARD x       [§0行20称修前PASS]              ->",
      act2("terminal", {"command": "cp " + DQ + TD + DQ + "=" + GUARD + " x"}))
print("p6) cp -dq tdir dq GUARD evil     [PM归因①称基线亦approve]       ->",
      act2("terminal", {"command": "cp -" + DQ + TD + DQ + " " + GUARD + " evil"}))
print("p7) cp '-t' GUARD x 整词空格式    [纳入3, 期望基线已approve]      ->",
      act2("terminal", {"command": "cp " + SQ + "-t" + SQ + " " + GUARD + " x"}))
print("p8) cp evil bs+CRLF GUARD         [§0行14称修前approve]           ->",
      act2("terminal", {"command": "cp evil " + B + CR + NL + GUARD}))
