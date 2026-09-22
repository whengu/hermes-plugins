# -*- coding: utf-8 -*-
"""round4 独立重放 + 攻击面第一批：六项修复到位性（round2 原始复现场景重放）
+ 修复引入面：目录形态判定、from-import 门、rsync 读方向、workdir+cwd 双键。"""
import importlib.util, os
spec = importlib.util.spec_from_file_location("wg4", "handler.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
os.environ["HERMES_HOME"] = r"D:\myagent" + chr(92) + ".hermes"
S = chr(92); HOME = "D:" + S + "myagent" + S + ".hermes"
CFG = HOME + S + "config.yaml"; PLG = "D:/myagent/.hermes/plugins/write-guard"
q = chr(34); tq = chr(39)*3
def act(tool, args):
    r = h.on_pre_tool_call(tool, args)
    return (r or {}).get("action") or "PASS"
ok=0; bad=[]
def chk(tag, got, exp):
    global ok
    if got==exp: ok+=1; print("  OK   %-52s -> %s" % (tag, got))
    else: bad.append(tag); print("  FAIL %-52s got %-6s want %s" % (tag, got, exp))

print("== R1 C-1 workdir（真实 schema 键名，round2 假绿场景重放）==")
chk("C: workdir 指临时目录", act("terminal",{"command":"touch ok","workdir":"D:"+S+"tmp"}), "block")
chk("A: workdir=home + 相对重定向", act("terminal",{"command":"echo hi > config.yaml","workdir":HOME}), "block")
chk("A: workdir=home + 相对 cp", act("terminal",{"command":"cp k.yaml settings.json","workdir":HOME}), "approve")
chk("负例 workdir=workspace", act("terminal",{"command":"echo hi > config.yaml","workdir":"D:"+S+"myagent"+S+"workspace"}), "PASS")
chk("cwd 死键指 home+相对写(平台实际不生效)", act("terminal",{"command":"echo hi > config.yaml","cwd":HOME}), "PASS")
chk("cwd 死键指 tmp(误拦面观察)", act("terminal",{"command":"touch ok","cwd":"D:"+S+"tmp"}), "block")
chk("workdir 非字符串", act("terminal",{"command":"ls","workdir":{"a":1}}), "PASS")
chk("workdir 相对形态", act("terminal",{"command":"echo hi > config.yaml","workdir":"sub"}), "PASS")

print("== R2 H-1 目录目标 + 形态边界 ==")
chk("cp x <home>/plugins/write-guard/ (尾斜杠)", act("terminal",{"command":"cp handler.py "+PLG+"/"}), "approve")
chk("cp x <home>/plugins/write-guard  (无尾斜杠) ← 边界", act("terminal",{"command":"cp handler.py "+PLG}), "approve")
chk("cp x <home>/ (home 本身带斜杠)", act("terminal",{"command":"cp a.yaml "+HOME+"/"}), "approve")
chk("cp x <home>   (home 无斜杠)", act("terminal",{"command":"cp a.yaml "+HOME}), "approve")
chk("cp -t <home>/plugins/write-guard/ x.py", act("terminal",{"command":"cp -t "+PLG+"/ handler.py"}), "approve")
chk("反斜杠尾分隔 cp x <dir>\\", act("terminal",{"command":"cp handler.py "+PLG.replace("/",S)+S}), "approve")
chk("负例 cat <dir>/", act("terminal",{"command":"cat "+PLG+"/"}), "PASS")
chk("负例 cp x workspace/sub/ (home 外目录)", act("terminal",{"command":"cp x.py D:/myagent/workspace/sub/"}), "PASS")
chk("H-1 变体: 目标带双引号+尾斜杠", act("terminal",{"command":"cp handler.py "+q+PLG+"/"+q}), "approve")
chk("H-1 变体: profiles/developer 目录", act("terminal",{"command":"cp x.yaml D:/myagent/.hermes/profiles/developer/"}), "approve")

print("== R3 N-4 递归基准传递（多层）==")
chk("bash -c 相对写 + workdir", act("terminal",{"command":"bash -c "+q+"echo x > config.yaml"+q,"workdir":HOME}), "block")
chk("python -c 绝对写", act("terminal",{"command":"python -c "+q+"open('"+CFG+"','w')"+q}), "block")
chk("python -c 相对写 + workdir", act("terminal",{"command":"python -c "+q+"open('config.yaml','w')"+q,"workdir":HOME}), "block")
chk("python -c 套 os.system 相对写 + workdir", act("terminal",{"command":"python -c "+q+"import os; os.system('echo x > config.yaml')"+q,"workdir":HOME}), "block")
chk("两层 bash -c 嵌套绝对写", act("terminal",{"command":"bash -c "+q+"bash -c 'echo x > "+CFG+"'"+q}), "block")
chk("两层 bash -c 嵌套相对写+workdir ← 二跳基准", act("terminal",{"command":"bash -c "+q+"bash -c 'echo x > config.yaml'"+q,"workdir":HOME}), "block")
chk("cmd /c 绝对重定向", act("terminal",{"command":"cmd /c "+q+"echo x > "+CFG+q}), "block")
chk("pwsh -Command 绝对 Set-Content", act("terminal",{"command":"pwsh -Command "+q+"Set-Content -Path "+CFG+" -Value x"+q}), "block")

print("== R4 N-1 shell 提取族 + from-import 门 ==")
def EC(c): return act("execute_code",{"code":c})
chk("os.getstatusoutput", EC("import os"+chr(10)+"os.getstatusoutput('echo x > "+CFG+"')"), "block")
chk("os.popen", EC("import os"+chr(10)+"os.popen('echo x > "+CFG+"')"), "block")
chk("from subprocess import run", EC("from subprocess import run"+chr(10)+"run('echo x > "+CFG+"', shell=True)"), "block")
chk("from subprocess import Popen", EC("from subprocess import Popen"+chr(10)+"Popen('echo x > "+CFG+"', shell=True)"), "block")
chk("负例 无 import 业务 run()", EC("def run(x): return x"+chr(10)+"run('echo x > "+CFG+"')"), "PASS")
chk("攻击A 别名导入 import subprocess as sp", EC("import subprocess as sp"+chr(10)+"sp.run('echo x > "+CFG+"', shell=True)"), "block")
chk("攻击B 别名 from import run as r", EC("from subprocess import run as r"+chr(10)+"r('echo x > "+CFG+"', shell=True)"), "block")
chk("攻击C 注释行 from-import 开闸(误拦观察)", EC("# 例: from subprocess import run 已废弃"+chr(10)+"run('echo x > "+CFG+"')"), "block")
chk("subprocess.run list 形态", EC("import subprocess"+chr(10)+"subprocess.run(['cp','a.yaml','"+CFG+"'])"), "approve")
chk("os.spawnl argv 族(声明边界)", EC("import os"+chr(10)+"os.spawnl(os.P_WAIT,'cp','cp','a.yaml','"+CFG+"')"), "PASS")
chk("os.execl argv 族(声明边界)", EC("import os"+chr(10)+"os.execl('/bin/sh','sh','-c','echo x > "+CFG+"')"), "PASS")

print("== R5 N-3 三引号折叠 + 副作用 ==")
chk("open(三引号,'w')", EC("open("+tq+CFG+tq+", 'w')"), "block")
chk("open(三DQ,'w')", EC("open("+chr(34)*3+CFG+chr(34)*3+", 'w')"), "block")
chk("Path(三引号).write_text", EC("Path("+tq+CFG+tq+").write_text('x')"), "block")
chk("os.system(三引号)", EC("import os"+chr(10)+"os.system("+tq+"echo x > "+CFG+tq+")"), "block")
chk("shutil.copy(三引号)", EC("import shutil"+chr(10)+"shutil.copy("+tq+"a"+tq+", "+tq+CFG+tq+")"), "approve")
chk("副作用: docstring 内嵌写文本(误拦观察)", EC(chr(34)*3+"教程: 用 open('"+CFG+"','w') 写入"+chr(34)*3+chr(10)+"pass"), "block")
chk("副作用: 相邻字面量拼接", EC("os.system('echo x > D:/myagent/.hermes/conf' 'ig.yaml')"), "block")

print("== R6 N-5 代码内工具调用 + N-6 rsync 读方向 ==")
chk("write_file 位置参", EC("write_file('"+CFG+"', 'evil')"), "block")
chk("hermes_tools.write_file(path=)", EC("from hermes_tools import write_file"+chr(10)+"write_file(path='"+CFG+"', content='x')"), "block")
chk("dict 形 path 键", EC("call({'path': '"+CFG+"', 'content': 'x'})"), "block")
chk("负例 dict path=workspace", EC("cfg = {'path': 'D:/myagent/workspace/a.md'}"), "PASS")
chk("rsync 写目标", act("terminal",{"command":"rsync a.yaml D:/myagent/.hermes/config.yaml"}), "approve")
chk("rsync 读源(末位非受保护)", act("terminal",{"command":"rsync D:/myagent/.hermes/config.yaml backup/"}), "PASS")
chk("rsync 读目录(尾斜杠源,末位非保护)", act("terminal",{"command":"rsync D:/myagent/.hermes/plugins/write-guard/ local/"}), "PASS")
chk("rsync -a --delete src/ <home>/plugins/write-guard/", act("terminal",{"command":"rsync -a --delete src/ "+PLG+"/"}), "approve")
chk("robocopy 实参序(目标第2位,声明边界)", act("terminal",{"command":"robocopy src D:/myagent/.hermes config.yaml"}), "PASS")
print()
print("通过", ok, "失败", len(bad))
for b in bad: print("   BAD:", b)
