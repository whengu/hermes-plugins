# round7 质量复审探针（audit-round7-qual）：NL 归一顺序 / Q-6-1 面 / Q-6-2 残面 / 引号形 FP
# 载荷全部落盘在本文件（教训①），执行命令行零载荷。
import importlib.util, os

B = chr(92); NL = chr(10); CR = chr(13); SQ = chr(39); DQ = chr(34)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
spec = importlib.util.spec_from_file_location(
    "wgq", "D:" + B + "myagent" + B + "workspace" + B + "write-guard" + B + "handler.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)

HOME = "D:/myagent/.hermes"
GUARD = HOME + "/plugins/write-guard"
CFG = HOME + "/config.yaml"


def act(tool, args):
    r = h.on_pre_tool_call(tool, args)
    return (r or {}).get("action") or "PASS"


def chk(tag, got, want):
    mark = "ok  " if got == want else "DIFF"
    print(mark + " " + tag.ljust(60) + " -> " + str(got) + ("" if got == want else "   [want " + want + "]"))


print("== P-A NL/续行归一 ==")
chk("P-A1 echo a+双反斜杠+LF+cp GUARD（shell 中 \\ 为字面量、LF 仍分隔→应 approve）",
    act("terminal", {"command": "echo a" + B + B + NL + "cp evil " + GUARD}), "approve")
chk("P-A1b 对照 单反斜杠+LF 续行（现状 approve）",
    act("terminal", {"command": "echo a" + B + NL + "cp evil " + GUARD}), "approve")
chk("P-A2 双反斜杠+LF truncate CFG（应 block）",
    act("terminal", {"command": "ls; touch f" + B + B + NL + "truncate -s 0 " + CFG}), "block")
chk("P-A3 单反斜杠+CRLF cp GUARD（归一顺序：先 \\n 后 \\r\\n 是否漏）",
    act("terminal", {"command": "cp evil " + B + CR + NL + GUARD}), "approve")
chk("P-A4 双反斜杠+CRLF cp GUARD",
    act("terminal", {"command": "echo a" + B + B + CR + NL + "cp evil " + GUARD}), "approve")
chk("P-A5 单反斜杠+裸CR cp GUARD（bash 语义 \\CR 非分隔符；文档未声明）",
    act("terminal", {"command": "cp evil " + B + CR + GUARD}), "PASS")

print("== P-B os.system 内 \\n 转义字面（Python 字符串求值后为真换行；守卫视图不换行）==")
code = ("import os" + NL
        + "os.system(" + DQ + "ls" + B + NL + "cp evil " + GUARD + " " + CFG + DQ + ")")
chk("P-B1 os.system('ls\\n cp evil …')（execute_code 内嵌 shell 面）",
    act("execute_code", {"code": code}), "PASS")
code2 = ("import os" + NL
         + "os.system(" + DQ + "cp evil " + GUARD + DQ + ")")
chk("P-B2 对照 单行 os.system cp GUARD（应 approve）",
    act("execute_code", {"code": code2}), "approve")

print("== P-C Q-6-1 粘连提取 getopt 语义 ==")
chk("P-C1 cp -tstage x（真 getopt: -s -t age → 目标 cwd/age 非 home → 放行）",
    act("terminal", {"command": "cp -tstage x"}), "PASS")
chk("P-C2 cd HOME && cp -tstage x（age=home 内 → Q-6-1 按整串判 approve；真 shell 也写 home）",
    act("terminal", {"command": "cd " + HOME + " && cp -tstage x"}), "approve")
chk("P-C3 cp -tr GUARD x（已登记目标歧义负例维持放行）",
    act("terminal", {"command": "cp -tr " + GUARD + " x"}), "PASS")
chk("P-C4 tar -tD:/somefile（非 cp/install 门挡 → 不误伤归档读）",
    act("terminal", {"command": "tar -tD:/somefile"}), "PASS")
chk("P-C5 ls -tD:/myagent（未知命令粘连 -t 门挡）",
    act("terminal", {"command": "ls -t" + HOME}), "PASS")
chk("P-C6 install -t=GUARD y（-t= 粘连）",
    act("terminal", {"command": "install -t=" + GUARD + " y"}), "approve")
chk("P-C7 cp \"-t\" GUARD evil 双引号形",
    act("terminal", {"command": "cp " + DQ + "-t" + DQ + " " + GUARD + " evil"}), "approve")

print("== P-D 引号选项形误命中面 ==")
chk("P-D1 cp '-t' CFG out/（'-t' 是被复制文件名、CFG 源位；保守扩面=approve 可接受？）",
    act("terminal", {"command": "cp " + SQ + "-t" + SQ + " " + CFG + " out/"}), "approve")
chk("P-D2 grep '-t' CFG（非 cp 族不触发）",
    act("terminal", {"command": "grep " + SQ + "-t" + SQ + " " + CFG}), "PASS")
chk("P-D3 cp 前文含 '--target-directory' 文本的文件名（token 级 FP 探测）",
    act("terminal", {"command": "cp x" + SQ + "--target-directory" + SQ + "y " + HOME + "/logs/a.txt out/"}), "PASS")

print("== P-E Q-6-2 收敛残面 + 引号感知负例 ==")
chk("P-E1 write_file plugins/write-guard-old/handler.py（段边界→放行）",
    act("write_file", {"path": HOME + "/plugins/write-guard-old" + B + "handler.py", "content": "x"}), "PASS")
chk("P-E2 cp evil GUARD-old（末位=C4 泛化保守 approve）",
    act("terminal", {"command": "cp evil.py D:" + B + B + "/myagent/.hermes/plugins/write-guard-old/f"}), "approve")
chk("P-E3 单引号跨行 echo 'a<NL>b' 后接 cp GUARD（引号感知不切→整体判仍 approve）",
    act("terminal", {"command": "echo " + SQ + "a" + NL + "b" + SQ + NL + "cp evil " + GUARD}), "approve")
chk("P-E4 heredoc 体含 cp GUARD 行（heredoc 边界未声明：cat>CFG 首段即 block）",
    act("terminal", {"command": "cat " + B + "." + B + "/" + CFG.replace("/", B) + " <<" + SQ + "EOF" + SQ + NL + "cp evil " + GUARD + NL + "EOF"}), "block")
chk("P-E5 execute_code 正则字面量含真换行符（不误伤）",
    act("execute_code", {"code": "import re" + NL + "re.split('a" + NL + "b', s)"}), "PASS")

print("== P-F CHANGELOG 名实抽查 ==")
chk("P-F1 CHANGELOG 称 r6_d 仿真验证换行分段零回潮：裸CR-only 分段现状",
    act("terminal", {"command": "ls" + CR + "cp evil " + GUARD}), "approve")
chk("P-F2 install -t 粘连 HOME（非 guard 目录、home 本体）",
    act("terminal", {"command": "install -t" + HOME + " x"}), "approve")
