# -*- coding: utf-8 -*-
import importlib.util, os, sys, hashlib
sys.path.insert(0, r"D:\myagent\workspace\write-guard")
os.environ["HERMES_HOME"] = r"D:\myagent\.hermes"
os.chdir(r"D:\myagent\workspace")
spec = importlib.util.spec_from_file_location("wg5e", r"D:\myagent\workspace\write-guard\handler.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
NL = chr(10); DQ = chr(34)
HOME = "D:/myagent/.hermes"; GUARD = HOME + "/plugins/write-guard"
def act(tool, args):
    r = h.on_pre_tool_call(tool, args)
    return (r or {}).get("action") or "PASS"
def T(c): return act("terminal", {"command": c})
print("== D6 -t 变体 ==")
for tag, c in [
  ("cp --target-directory guard x", "cp --target-directory "+GUARD+" x"),
  ("cp --target-directory=guard x", "cp --target-directory="+GUARD+" x"),
  ("cp -rt guard x", "cp -rt "+GUARD+" x"),
  ("cp -r -t guard x 对照", "cp -r -t "+GUARD+" x"),
  ("install --target-directory home x", "install --target-directory "+HOME+" x"),
]:
    print("  %-38s -> %s" % (tag, T(c)))
print("== D7 无斜杠 home 子目录族 ==")
for c in ["cp x "+HOME+"/profiles", "cp x "+HOME+"/profiles/", "cp x "+HOME+"/logs"]:
    print("  %-40s -> %s" % (c, T(c)))
print("== D5 deploy 镜像推导（纯 Path 演算，不落盘）==")
from pathlib import Path
import deploy
dst = Path(r"D:\myagent\.hermes\plugins\write-guard")
pr = dst.parent.parent / "profiles"
print("  profiles_root:", pr, "is_dir:", pr.is_dir())
print("  同步目标:", [str(x.relative_to(pr)) for x in sorted(pr.iterdir()) if (x/"plugins"/"write-guard").is_dir()])
d2 = Path("E:/somewhere/plugins/write-guard")
print("  自定义 dst ->", d2.parent.parent/"profiles", "(is_dir:", (d2.parent.parent/"profiles").is_dir(), "-> 跳过)")
print("  FILES:", deploy.FILES)
print("== D8 profile 副本哈希一致性复核（OBS-1 闭环）==")
def sha(p):
    try: return hashlib.sha256(open(p,'rb').read()).hexdigest()[:12]
    except Exception: return "MISS"
for name, p in [
  ("arch/init", r"D:\myagent\.hermes\profiles\architect\plugins\write-guard\__init__.py"),
  ("arch/yaml", r"D:\myagent\.hermes\profiles\architect\plugins\write-guard\plugin.yaml"),
  ("dev/init",  r"D:\myagent\.hermes\profiles\developer\plugins\write-guard\__init__.py"),
  ("dev/yaml",  r"D:\myagent\.hermes\profiles\developer\plugins\write-guard\plugin.yaml"),
  ("main/init", r"D:\myagent\.hermes\plugins\write-guard\__init__.py"),
  ("main/yaml", r"D:\myagent\.hermes\plugins\write-guard\plugin.yaml"),
]:
    print("  %-10s %s %s" % (name, sha(p), p))
print("== D9 换行旁路对内嵌链传导 ==")
print("  bash -c 多行体 cp:", T("bash -c "+DQ+"true"+NL+"cp evil "+GUARD+DQ))
print("  对照 bash -c 单行体 cp:", T("bash -c "+DQ+"cp evil "+GUARD+DQ))
print("  os.system 多行(cp 守卫):", act("execute_code", {"code": "import os"+NL+"os.system('true"+NL+"cp evil "+GUARD+"')"}))
