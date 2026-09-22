# -*- coding: utf-8 -*-
"""round5 独立重放（A 卷）：round4 双路报告全部原始复现场景 + _verify_r5 声称项，
期望值按 round5 意图修正（robocopy=声明边界 PASS、SED/DD/PERL 大写=block、
workdir 相对=block、别名门=block）。不采信自述。"""
import importlib.util, os, sys
os.environ["HERMES_HOME"] = r"D:\myagent" + chr(92) + ".hermes"
os.chdir(r"D:\myagent\workspace")   # 与 _verify_r5 同基准（../.hermes 场景依赖进程 cwd）
spec = importlib.util.spec_from_file_location("wg5", r"D:\myagent\workspace\write-guard\handler.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
S = chr(92); HOME = "D:" + S + "myagent" + S + ".hermes"
CFG = HOME + S + "config.yaml"; PLG = "D:/myagent/.hermes/plugins/write-guard"
q = chr(34); tq = chr(39)*3; nl = chr(10)
def act(tool, args):
    r = h.on_pre_tool_call(tool, args)
    return (r or {}).get("action") or "PASS"
def EC(c): return act("execute_code", {"code": c})
ok=0; bad=[]
def chk(tag, got, exp):
    global ok
    if got==exp: ok+=1; print("  OK   %-58s -> %s" % (tag, got))
    else: bad.append(tag); print("  FAIL %-58s got %-6s want %s" % (tag, got, exp))

print("== R1 C-1/F-2 workdir（round5：相对形态已绝对化）==")
chk("C: workdir 指临时目录", act("terminal",{"command":"touch ok","workdir":"D:"+S+"tmp"}), "block")
chk("A: workdir=home + 相对重定向", act("terminal",{"command":"echo hi > config.yaml","workdir":HOME}), "block")
chk("A: workdir=home + 相对 cp", act("terminal",{"command":"cp k.yaml settings.json","workdir":HOME}), "approve")
chk("负例 workdir=workspace", act("terminal",{"command":"echo hi > config.yaml","workdir":"D:"+S+"myagent"+S+"workspace"}), "PASS")
chk("cwd 死键指 home+相对写(登记:平台不生效)", act("terminal",{"command":"echo hi > config.yaml","cwd":HOME}), "PASS")
chk("cwd 死键指 tmp(C 误拦=登记面)", act("terminal",{"command":"touch ok","cwd":"D:"+S+"tmp"}), "block")
chk("workdir 非字符串", act("terminal",{"command":"ls","workdir":{"a":1}}), "PASS")
chk("workdir 相对形态(非危险)", act("terminal",{"command":"echo hi > config.yaml","workdir":"sub"}), "PASS")
chk("F-2: workdir=../.hermes + 相对写", act("terminal",{"command":"echo hi > config.yaml","workdir":"../.hermes"}), "block")
chk("F-2: workdir 反斜杠相对 .."+S+".hermes", act("terminal",{"command":"echo hi > config.yaml","workdir":".."+S+".hermes"}), "block")
chk("负例: workdir=../workspace + 相对写", act("terminal",{"command":"echo hi > config.yaml","workdir":".."+S+"workspace"}), "PASS")

print("== R2 H-1/F-1 目录目标（round5：无尾分隔符守卫目录已收）==")
chk("cp x <guard>/ (尾斜杠)", act("terminal",{"command":"cp handler.py "+PLG+"/"}), "approve")
chk("cp x <guard>  (无尾斜杠)", act("terminal",{"command":"cp handler.py "+PLG}), "approve")
chk("cp x <home>/", act("terminal",{"command":"cp a.yaml "+HOME+"/"}), "approve")
chk("cp x <home>  (无斜杠)", act("terminal",{"command":"cp a.yaml "+HOME}), "approve")
chk("cp -t <guard>/ x.py", act("terminal",{"command":"cp -t "+PLG+"/ handler.py"}), "approve")
chk("cp -t <guard> x.py (无斜杠)", act("terminal",{"command":"cp -t "+PLG+" handler.py"}), "approve")
chk("反斜杠无尾分隔 cp x <guard>"+S.replace(S,S*2), act("terminal",{"command":"cp handler.py "+(HOME+S+"plugins"+S+"write-guard").replace(S,S*2)}), "approve")
chk("单反斜杠 cp x D:"+S+"myagent"+S+".hermes"+S+"plugins"+S+"write-guard", act("terminal",{"command":"cp handler.py D:"+S+"myagent"+S+".hermes"+S+"plugins"+S+"write-guard"}), "approve")
chk("负例 cat <guard>/", act("terminal",{"command":"cat "+PLG+"/"}), "PASS")
chk("负例 cat <guard> (无斜杠,round5新收面)", act("terminal",{"command":"cat "+PLG}), "PASS")
chk("负例 ls <guard>", act("terminal",{"command":"ls "+PLG}), "PASS")
chk("负例 grep <guard>", act("terminal",{"command":"grep -r x "+PLG}), "PASS")
chk("负例 cp x workspace/sub/ (home 外)", act("terminal",{"command":"cp x.py D:/myagent/workspace/sub/"}), "PASS")
chk("H-1 变体: 目标双引号+尾斜杠", act("terminal",{"command":"cp handler.py "+q+PLG+"/"+q}), "approve")
chk("H-1 变体: profiles/developer 目录", act("terminal",{"command":"cp x.yaml D:/myagent/.hermes/profiles/developer/"}), "approve")
chk("F-1 大写盘符/大小写混排目标", act("terminal",{"command":"cp x D:/MYAGENT/.HERMES/PLUGINS/Write-Guard"}), "approve")

print("== R3 N-4 递归基准 + F-2 组合（workdir 相对 + 嵌套）==")
chk("bash -c 相对写 + workdir=home", act("terminal",{"command":"bash -c "+q+"echo x > config.yaml"+q,"workdir":HOME}), "block")
chk("bash -c 相对写 + workdir=../.hermes", act("terminal",{"command":"bash -c "+q+"echo x > config.yaml"+q,"workdir":"../.hermes"}), "block")
chk("python -c 绝对写", act("terminal",{"command":"python -c "+q+"open('"+CFG+"','w')"+q}), "block")
chk("python -c 相对写 + workdir", act("terminal",{"command":"python -c "+q+"open('config.yaml','w')"+q,"workdir":HOME}), "block")
chk("python -c 套 os.system 相对写 + workdir", act("terminal",{"command":"python -c "+q+"import os; os.system('echo x > config.yaml')"+q,"workdir":HOME}), "block")
chk("两层 bash -c 嵌套绝对写", act("terminal",{"command":"bash -c "+q+"bash -c 'echo x > "+CFG+"'"+q}), "block")
chk("两层 bash -c 嵌套相对写+workdir 二跳", act("terminal",{"command":"bash -c "+q+"bash -c 'echo x > config.yaml'"+q,"workdir":HOME}), "block")
chk("cmd /c 绝对重定向", act("terminal",{"command":"cmd /c "+q+"echo x > "+CFG+q}), "block")
chk("pwsh -Command 绝对 Set-Content", act("terminal",{"command":"pwsh -Command "+q+"Set-Content -Path "+CFG+" -Value x"+q}), "block")

print("== R4 N-1/F-3 shell 提取族 + 门四形态 ==")
chk("os.getstatusoutput", EC("import os"+nl+"os.getstatusoutput('echo x > "+CFG+"')"), "block")
chk("os.popen", EC("import os"+nl+"os.popen('echo x > "+CFG+"')"), "block")
chk("from subprocess import run", EC("from subprocess import run"+nl+"run('echo x > "+CFG+"', shell=True)"), "block")
chk("from subprocess import Popen", EC("from subprocess import Popen"+nl+"Popen('echo x > "+CFG+"', shell=True)"), "block")
chk("负例 无 import 业务 run()", EC("def run(x): return x"+nl+"run('echo x > "+CFG+"')"), "PASS")
chk("F-3: import subprocess as sp; sp.run", EC("import subprocess as sp"+nl+"sp.run('echo x > "+CFG+"', shell=True)"), "block")
chk("F-3: from import run as r", EC("from subprocess import run as r"+nl+"r('echo x > "+CFG+"', shell=True)"), "block")
chk("F-3: from import *", EC("from subprocess import *"+nl+"run('echo x > "+CFG+"', shell=True)"), "block")
chk("F-3: 多行括号 import", EC("from subprocess import ("+nl+"    run,"+nl+")"+nl+"run('echo x > "+CFG+"', shell=True)"), "block")
chk("注释行 from-import 开闸(登记:误拦可接受)", EC("# 例: from subprocess import run 已废弃"+nl+"run('echo x > "+CFG+"')"), "block")
chk("subprocess.run list 形态", EC("import subprocess"+nl+"subprocess.run(['cp','a.yaml','"+CFG+"'])"), "approve")
chk("os.spawnl argv 族(声明边界)", EC("import os"+nl+"os.spawnl(os.P_WAIT,'cp','cp','a.yaml','"+CFG+"')"), "PASS")
chk("os.execl argv 族(声明边界)", EC("import os"+nl+"os.execl('/bin/sh','sh','-c','echo x > "+CFG+"')"), "PASS")
chk("F-3 负例 业务 run() 不误拦(_verify L57)", EC("def run():"+nl+"    pass"+nl+"run()"), "PASS")
chk("F-3 负例 裸 run('job')", EC("run('job')"), "PASS")

print("== R5 N-3/F-8 三引号折叠（登记面核对：两向均维持登记）==")
chk("open(三SQ,'w')", EC("open("+tq+CFG+tq+", 'w')"), "block")
chk("open(三DQ,'w')", EC("open("+chr(34)*3+CFG+chr(34)*3+", 'w')"), "block")
chk("Path(三SQ).write_text", EC("Path("+tq+CFG+tq+").write_text('x')"), "block")
chk("os.system(三引号)", EC("import os"+nl+"os.system("+tq+"echo x > "+CFG+tq+")"), "block")
chk("shutil.copy(三引号)", EC("import shutil"+nl+"shutil.copy("+tq+"a"+tq+", "+tq+CFG+tq+")"), "approve")
chk("F-8向1 docstring 误拦(登记)", EC(chr(34)*3+"教程: 用 open('"+CFG+"','w') 写入"+chr(34)*3+nl+"pass"), "block")
chk("F-8向2 相邻字面量拼接漏(登记)", EC("import os"+nl+"os.system('echo x > D:/myagent/.hermes/conf' 'ig.yaml')"), "PASS")

print("== R6 N-5/N-6/R4-1/F-4/F-5 ==")
chk("write_file 位置参", EC("write_file('"+CFG+"', 'evil')"), "block")
chk("hermes_tools.write_file(path=)", EC("from hermes_tools import write_file"+nl+"write_file(path='"+CFG+"', content='x')"), "block")
chk("dict 形 path 键", EC("call({'path': '"+CFG+"', 'content': 'x'})"), "block")
chk("负例 dict path=workspace", EC("cfg = {'path': 'D:/myagent/workspace/a.md'}"), "PASS")
chk("rsync 写目标", act("terminal",{"command":"rsync a.yaml D:/myagent/.hermes/config.yaml"}), "approve")
chk("rsync 读源(末位非受保护)", act("terminal",{"command":"rsync D:/myagent/.hermes/config.yaml backup/"}), "PASS")
chk("rsync 读目录(尾斜杠源)", act("terminal",{"command":"rsync D:/myagent/.hermes/plugins/write-guard/ local/"}), "PASS")
chk("rsync -a --delete src/ <guard>/", act("terminal",{"command":"rsync -a --delete src/ "+PLG+"/"}), "approve")
chk("R4-1: rsync -t <CFG> backup/ (读向)", act("terminal",{"command":"rsync -t "+CFG+" backup/"}), "PASS")
chk("R4-1: install -t <home> x (写向)", act("terminal",{"command":"install -t D:/myagent/.hermes x.yaml"}), "approve")
chk("F-4: robocopy 三参(撤出,声明边界)", act("terminal",{"command":"robocopy src D:/myagent/.hermes config.yaml"}), "PASS")
chk("F-5: SED -i 大写", act("terminal",{"command":"SED -i 's/a/b/' "+CFG}), "block")
chk("F-5: PERL -pi 大写", act("terminal",{"command":"PERL -pi -e 's/a/b/' "+CFG}), "block")
chk("F-5: DD of= 大写", act("terminal",{"command":"DD of="+CFG}), "block")
chk("F-5 负例: SED -n 读向", act("terminal",{"command":"SED -n '1p' "+CFG}), "PASS")

print("== R7 F-7 args 收敛（异常链必须消失）==")
import logging, io
buf = io.StringIO()
hdl = logging.StreamHandler(buf); hdl.setLevel(logging.ERROR)
lg = h.logger
lg.addHandler(hdl); lg.propagate = False
for v in (None, "str", [1], 42, 0, ""):
    chk("args=%r terminal" % v, act("terminal", v), "PASS")
for v in (None, "str", [1], 42):
    chk("args=%r write_file" % v, act("write_file", v), "PASS")
    chk("args=%r execute_code" % v, act("execute_code", v), "PASS")
    chk("args=%r memory" % v, act("memory", v), "approve")   # B 按工具名，参数无关
    chk("args=%r 未知工具" % v, act("chrome_click", v), "PASS")
err_txt = buf.getvalue()
chk("无 ERROR 级日志(守卫零异常)", "yes" if not err_txt else "traceback!", "yes")
if err_txt: print(err_txt[:800])

print()
print("通过", ok, "失败", len(bad))
for b in bad: print("   BAD:", b)
