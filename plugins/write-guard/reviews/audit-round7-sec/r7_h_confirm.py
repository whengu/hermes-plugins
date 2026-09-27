# -*- coding: utf-8 -*-
"""H 卷：D1/E2 旁路实证的 shell 真值 + 残余定向形。
H1 引号剥离真值：cp -"t" sub f1 是否真的以 sub 为目标（旁路可利用性实证）
H2 cp -"target-directory" 半混长形
H3 \\+LF 奇偶：POSIX 真值补测（printf+cp /dev/null）
H4 守卫D \\<LF> 形（第一步 replace 命中→block 吗）
H5 "--target" 前缀假阳性探测
"""
import importlib.util, os, subprocess
os.environ["HERMES_HOME"] = r"D:\myagent\.hermes"
os.chdir(r"D:\myagent\workspace")
spec = importlib.util.spec_from_file_location("wg7h", r"D:\myagent\workspace\write-guard\handler.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
NL, CR, B, Q = chr(10), chr(13), chr(92), chr(34)
HOME = "D:/myagent/.hermes"
GUARD = HOME + "/plugins/write-guard"
T = r"D:\myagent\workspace\_r2tmp"
os.makedirs(T, exist_ok=True)
def act(tool, args):
    r = h.on_pre_tool_call(tool, args)
    return (r or {}).get("action") or "PASS"
def TC(c): return act("terminal", {"command": c})

print("== H1 shell 真值：cp -\"t\" 半混引号，目标语义成立吗 ==")
sub = os.path.join(T, "hsub"); os.makedirs(sub, exist_ok=True)
for f in os.listdir(sub): os.remove(os.path.join(sub, f))
srcf = os.path.join(T, "hsrc.txt")
open(srcf, "w").write("payload")
r = subprocess.run(["bash", "-c",
    "cp -" + Q + "t" + Q + " " + sub.replace("\\", "/") + " " + srcf.replace("\\", "/")],
    capture_output=True, text=True, timeout=20)
moved = bool(os.listdir(sub)) and not os.path.exists(srcf)
print("  rc=%s stderr=%r src存活=%s 目标目录内容=%s => %s" % (
    r.returncode, r.stderr.strip()[:60], os.path.exists(srcf), os.listdir(sub),
    "SHELL 真按 -t 目标执行(旁路可利用)" if moved else "未移动"))
print("  守卫判定: ", TC("cp -" + Q + "t" + Q + " " + GUARD + " evil"), "(PASS=旁路实锤)")

print("== H2 半混长形 ==")
print("  cp -\"target-directory\" GUARD evil ->", TC("cp -" + Q + "target-directory" + Q + " " + GUARD + " evil"))
print("  shell 真值:", subprocess.run(["bash","-c","cp -"+Q+"target-directory"+Q+" "+sub.replace("\\","/")+" "+srcf.replace("\\","/")],capture_output=True,text=True).returncode, os.listdir(sub))
for f in os.listdir(sub): os.remove(os.path.join(sub, f))
print("  cp --target-dir\"ectory\" GUARD evil ->", TC("cp --target-dir" + Q + "ectory" + Q + " " + GUARD + " evil"))
print("  cp '-t'GUARD 连写(已 D6 拦) 对照; cp -t''GUARD? ->", TC("cp -t" + chr(39) + GUARD + chr(39) + " evil"))

print("== H3 POSIX 奇偶补证（本机 MSYS 已知 JOIN；文档语义预告）==")
print("  bash --version:", subprocess.run(["bash","--version"],capture_output=True,text=True).stdout.splitlines()[0])
for name, sep in [("\\+LF", B+NL), ("\\\\+LF", B*2+NL)]:
    mkf = os.path.join(T, "h3_%s" % name.strip(B)).replace("\\", "/")
    try: os.remove(mkf)
    except OSError: pass
    rr = subprocess.run(["bash","-c","cp /dev/null " + sep + "touch " + mkf],capture_output=True,text=True)
    print("  %-8s rc=%s marker=%s" % (name, rr.returncode, "CREATED" if os.path.exists(mkf) else "absent"))

print("== H4 守卫D 残余形 ==")
print("  D: hermes gateway \\<LF>restart      ->", TC("hermes gateway " + B + NL + "restart"), "(block=已对称)")
print("  D: hermes gateway \\<CRLF>restart    ->", TC("hermes gateway " + B + CR + NL + "restart"), "(PASS=漏 CRLF 形)")
print("  D: hermes gateway<CR><LF>restart 双真行 ->", TC("hermes gateway" + CR + NL + "restart"))
print("  D: 反引号/命令替换 echo `hermes gateway restart` ->", TC("echo " + chr(96) + "hermes gateway restart" + chr(96)))
print("  D: $() 内嵌 $(hermes gateway restart) ->", TC("X=$(hermes gateway restart)"))

print("== H5 QUOTED 假阳性探测 ==")
print("  grep \"--target\" file (前缀非全称) ->", TC("grep " + Q + "--target" + Q + " notes.txt"))
print("  cp '--targe' 't-directory' x ->", TC("cp '--targe' 't-directory' x"))
print("  读 home 文件带引号 -t: grep '-t' HOME/config.yaml ->", TC("grep '-t' " + HOME + "/config.yaml"))
print("  rm -rf 反缴械(非复制族,登记边界) cp 形对照: rm " + GUARD + "/handler.py ->", TC("rm " + GUARD + "/handler.py"))
print("  cat > guard/handler.py 重定向写(矩阵>分支) ->", TC("cat evil > " + GUARD + "/handler.py"))
print("  tee guard/handler.py ->", TC("echo x | tee " + GUARD + "/handler.py"))
