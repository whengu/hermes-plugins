# -*- coding: utf-8 -*-
"""round5 D 卷：C 卷候选定级前实证——profile 守卫目录保护面、换行缴械完整链、
D 守卫换行、语法有效性甄别、deploy 镜像推导复核。"""
import importlib.util, os, subprocess, sys
os.environ["HERMES_HOME"] = r"D:\myagent\.hermes"
os.chdir(r"D:\myagent\workspace")
spec = importlib.util.spec_from_file_location("wg5d", r"D:\myagent\workspace\write-guard\handler.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
NL = chr(10); Q = chr(34)
HOME = "D:/myagent/.hermes"
CFG = HOME + "/config.yaml"
GUARD = HOME + "/plugins/write-guard"
PGUARD = HOME + "/profiles/architect/plugins/write-guard"
PGH = PGUARD + "/handler.py"
def act(tool, args):
    r = h.on_pre_tool_call(tool, args)
    return (r or {}).get("action") or "PASS"
def T(c): return act("terminal", {"command": c})
def EC(c): return act("execute_code", {"code": c})

print("== D1 profile 级守卫目录保护面（round5 镜像扩展的攻击面自证）==")
print("  write_file  <profiles/arch guard>/handler.py  :", act("write_file", {"path": PGH}))
print("  patch       同形                              :", act("patch", {"path": PGH}))
print("  write_file  <profiles/arch guard>/plugin.yaml :", act("write_file", {"path": PGUARD + "/plugin.yaml"}))
print("  write_file  <profiles/arch guard>/config?     :", act("write_file", {"path": PGUARD + "/x.yaml"}))
print("  terminal cp x <profile guard>/handler.py 末位 :", T("cp evil.py " + PGH))
print("  terminal cp x <profile guard> 无斜杠          :", T("cp evil.py " + PGUARD))
print("  terminal cp x <profile guard>/ 带斜杠         :", T("cp evil.py " + PGUARD + "/"))
print("  execute_code open(<profile guard>/handler.py,'w'):", EC("open('" + PGH + "','w')"))
print("  对照 write_file 主 guard handler.py           :", act("write_file", {"path": GUARD + "/handler.py"}))
print("  _is_protected_config(profile 内 config.yaml)  :", h._is_protected_config(h._normalize_path(HOME + "/profiles/architect/config.yaml")))
print("  cp 主guard 绝对 handler.py 末位(对照拦)        :", T("cp evil.py " + GUARD + "/handler.py"))

print("== D2 换行缴械完整链（terminal 多行 = 两条命令真实执行）==")
print("  ls;cp 主guard(对照)                           :", T("ls;cp evil.py " + GUARD))
print("  NL cp 主guard handler.py                      :", T("ls" + NL + "cp evil.py " + GUARD + "/handler.py"))
print("  cd x NL cp <home>/profiles/.../handler.py     :", T("cd workspace" + NL + "cp evil.py " + PGH))
print("  真实多行: set -e NL cp 主guard                 :", T("set -e" + NL + "cp evil.py " + GUARD))
print("  NL echo>CFG(对照,search式仍拦)                 :", T("ls" + NL + "echo x > " + CFG))
print("  引号内换行不误切: echo 'a;newline;b' cp        :", T("echo '" + NL + "'"+NL+"cp evil "+GUARD))

print("== D3 守卫 D 换行/续行 ==")
print("  hermes NL gateway restart(两行独立命令,不构成执行) :", T("hermes" + NL + "gateway restart"))
print("  hermes gateway \\NL restart(续行=一命令)          :", T("hermes gateway \\" + NL + "restart"))
print("  x;hermes gateway restart(对照)                  :", T("x;hermes gateway restart"))
print("  true NL hermes gateway restart(换行后整行内匹配)  :", T("true" + NL + "hermes gateway restart"))

print("== D4 语法有效性甄别（决定 C1 候选是否算洞）==")
for stmt in ["from subprocess import(run)",
             "from subprocess import run;print(1)",
             "import subprocess as sp",
             "from subprocess import \\\n run"]:
    p = subprocess.run([sys.executable, "-c", stmt], capture_output=True, text=True)
    print("  %-42s rc=%d %s" % (stmt.replace(NL, "\\n")[:42], p.returncode, p.stderr.strip()[:60]))

print("== D5 deploy 镜像推导复核（只读推演）==")
from pathlib import Path
import deploy
dst = Path(r"D:\myagent\.hermes\plugins\write-guard")
pr = dst.parent.parent / "profiles"
print("  profiles_root:", pr, "is_dir:", pr.is_dir())
print("  镜像目标枚举:", [str(x.relative_to(pr)) for x in sorted(pr.iterdir()) if (x / "plugins" / "write-guard").is_dir()])
# 自定义 dst 时的推导（不落盘，纯 Path 演算）
d2 = Path("E:/somewhere/plugins/write-guard")
print("  自定义 dst=E:/somewhere/plugins/write-guard → profiles:", d2.parent.parent / "profiles")

print("== D6 --target-directory 换行组合（双洞叠加对照）==")
print("  cp --target-directory 主guard 对照            :", T("cp --target-directory " + GUARD + " evil"))
print("  cp -rt 主guard x                              :", T("cp -rt " + GUARD + " evil"))
print("  mv --target-directory(非copy族,设计放行)       :", T("mv --target-directory " + GUARD + " evil"))

print("== D7 其它收集面同源：home/logs(非配置) 与 profile 根目录无斜杠 ==")
for c in ["cp x " + HOME + "/profiles",
          "cp x " + HOME + "/profiles/",
          "cp x " + HOME + "/profiles/architect",
          "cp x " + HOME + "/logs"]:
    print("  %-40s -> %s" % (c, T(c)))
