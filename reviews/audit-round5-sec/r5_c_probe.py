# -*- coding: utf-8 -*-
"""round5 C 卷：B 卷候选的机制甄别 + 门残余形态 + 换行旁路矩阵 + 环境事实。"""
import importlib.util, os
os.environ["HERMES_HOME"] = r"D:\myagent\.hermes"
os.chdir(r"D:\myagent\workspace")
spec = importlib.util.spec_from_file_location("wg5c", r"D:\myagent\workspace\write-guard\handler.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
S = chr(92); NL = chr(10); Q = chr(34)
HOME = "D:/myagent/.hermes"
CFG = HOME + "/config.yaml"
GUARD = HOME + "/plugins/write-guard"
def act(tool, args):
    r = h.on_pre_tool_call(tool, args)
    return (r or {}).get("action") or "PASS"
def T(c): return act("terminal", {"command": c})
def EC(c): return act("execute_code", {"code": c})
nl = NL

print("== 环境事实：tilde 目标核实 ==")
print("  expanduser('~') =", os.path.expanduser("~"))
print("  USERPROFILE =", os.environ.get("USERPROFILE"), "| HOME =", os.environ.get("HOME"))
print("  norm(~/.hermes/plugins/write-guard) =", h._normalize_path("~/.hermes/plugins/write-guard"))
print("  guard 判定该 norm:", h._is_guard_dir_target(h._normalize_path("~/.hermes/plugins/write-guard")))
print("  => tilde 展开指向真实家目录(非 D:/myagent)时 PASS=正确（写入落点非守卫），不是洞")

print("== C1 门残余形态（F-3 之外还能怎么关闸）==")
print(" no-space paren  import(run)         :", EC("from subprocess import(run)"+nl+"run('echo x > "+CFG+"', shell=True)"))
print(" line-cont as    import subprocess \\<nl>as sp :", EC("import subprocess \\"+nl+"as sp"+nl+"sp.run('echo x > "+CFG+"', shell=True)"))
print(" line-cont from  from subprocess import \\<nl>run :", EC("from subprocess import \\"+nl+"run"+nl+"run('echo x > "+CFG+"', shell=True)"))
print(" line-cont 括号  from subprocess import (\\<nl> run,)", )
print("   ->", EC("from subprocess import (\\"+nl+"run,"+nl+")"+nl+"run('echo x > "+CFG+"', shell=True)"))
print(" 对照 常规无空格 as:", EC("from subprocess import run"+nl+"run('echo x > "+CFG+"', shell=True)"))
print(" semicolon 同行双语句 run(...);from-import 前置调用：")
print("   ->", EC("run('echo x > "+CFG+"', shell=True);from subprocess import run"))
print(" from 子模块 import run from subprocess as? (语法不存在) 跳过")
print(" 别名重建误拦面  sp 未 import 但业务同名 :", EC("sp = obj()"+nl+"sp.run('echo x > "+CFG+"')"))
print(" gate 开但无调用零误伤:", EC("import subprocess as sp"+nl+"x = 1"))
print(" DOTALL 过度: from-import 体跨到几百行后的 sp.", )
big = "import subprocess as sp"+nl+("z = 1"+nl)*5+"sp.run('echo x > "+CFG+"', shell=True)"
print("   ->", EC(big))

print("== C2 换行旁路矩阵（哪些分支被 \\n 穿透）==")
cases = [
 ("对照 ; 分", "ls;cp evil "+GUARD),
 ("对照 && 分", "ls && cp evil "+GUARD),
 ("换行 cp 守卫", "ls"+nl+"cp evil "+GUARD),
 ("换行 cp home子目录无斜杠", "ls"+nl+"cp config.yaml "+HOME+"/profiles/developer"),
 ("换行 cp home根无斜杠", "ls"+nl+"cp a.yaml "+HOME),
 ("换行 cp 带斜杠子目录", "ls"+nl+"cp a.yaml "+HOME+"/profiles/developer/"),
 ("换行 truncate", "ls"+nl+"truncate -s 0 "+CFG),
 ("换行 install", "ls"+nl+"install x "+CFG),
 ("换行 rsync", "ls"+nl+"rsync a "+CFG),
 ("换行 cp -t", "ls"+nl+"cp -t "+GUARD+" evil"),
 ("换行 sed -i(应仍拦,search式)", "ls"+nl+"sed -i 's/a/b/' "+CFG),
 ("换行 tee(应仍拦,prev词式)", "echo x | tee "+CFG),
 ("换行 >重定向(应仍拦)", "ls"+nl+"echo x > "+CFG),
 ("换行 python -c 内嵌", "ls"+nl+"python -c "+Q+"open('"+CFG+"','w')"+Q),
 ("bash -c 多行体", "bash -c "+Q+"ls"+nl+"cp evil "+GUARD+Q),
 ("换行 cp 读向负例", "ls"+nl+"cat "+GUARD),
]
for tag, c in cases:
    print("  %-34s -> %s" % (tag, T(c)))

print("== C3 -t 目标标志识别面（长形/粘连/簇）==")
for tag, c in [
  ("cp -t guard (拦)", "cp -t "+GUARD+" x"),
  ("cp --target-directory guard", "cp --target-directory "+GUARD+" x"),
  ("cp --target-directory=guard", "cp --target-directory="+GUARD+" x"),
  ("cp -rt guard x", "cp -rt "+GUARD+" x"),
  ("cp -a -t guard x", "cp -a -t "+GUARD+" x"),
  ("install --target-directory home", "install --target-directory "+HOME+" x"),
  ("rsync --rsync-path 无关负例", "rsync --delete a/ b/"),
  ("cp -T guard (大写T=不建目录GNU) ", "cp -T "+GUARD+" x"),
]:
    print("  %-38s -> %s" % (tag, T(c)))

print("== C4 home 内非 guard 子目录·无斜杠末位（round4 F-1 修法宽判腿核对）==")
for tag, c in [
  ("cp x <home>/profiles/developer", "cp cfg.yml "+HOME+"/profiles/developer"),
  ("同带斜杠", "cp cfg.yml "+HOME+"/profiles/developer/"),
  ("cp x <home>/plugins", "cp cfg.yml "+HOME+"/plugins"),
  ("同带斜杠", "cp cfg.yml "+HOME+"/plugins/"),
  ("cp x <home>/skills (非保护面)", "cp cfg.yml "+HOME+"/skills"),
  ("mv 同形(路径级不拦=设计)", "mv cfg.yml "+HOME+"/profiles/developer"),
  ("同 mv 带斜杠", "mv cfg.yml "+HOME+"/profiles/developer/"),
]:
    print("  %-38s -> %s" % (tag, T(c)))

print("== C5 F-7 收敛深面：args={} 时 C 兜底/A/D 行为 ==")
print("  unknown_tool args={}:", act("chrome_click", {}))
print("  terminal args={}:", act("terminal", {}))
print("  args 值为嵌套 dict 含 /tmp 字符串(未知工具兜底只扫一层):", act("chrome_take_screenshot", {"opts": {"path": "/tmp/x"}}))
print("  execute_code args={}:", act("execute_code", {}))
print("== C6 workdir 极端形态（F-2 残余）==")
for tag, wd, cmd in [
  ("workdir='..' + 相对写", "..", "echo x > .hermes/config.yaml"),
  ("workdir='.' ", ".", "echo x > config.yaml"),
  ("workdir='~' ", "~", "echo x > config.yaml"),
  ("workdir=$HERMES_HOME ", "$HERMES_HOME", "echo x > config.yaml"),
  ("workdir 双盘符 //?/ ", "//?/D:/myagent/.hermes", "echo x > config.yaml"),
  ("workdir 尾随空格 ", HOME+"  ", "echo x > config.yaml"),
]:
    print("  %-24s -> %s" % (tag, act("terminal", {"command": cmd, "workdir": wd})))
