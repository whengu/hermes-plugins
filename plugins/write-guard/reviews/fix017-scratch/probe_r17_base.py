# round17 施工前探针：绝对形 -t 族基线（改动1 各点接视图后须保持不漂移）
import importlib.util, os
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
spec = importlib.util.spec_from_file_location("w", r"D:\myagent\workspace\write-guard\handler.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
H = "D:" + B + "myagent" + B + ".hermes"
def call(cmd):
    r = m.on_pre_tool_call("terminal", {"command": cmd}, "pm")
    return "PASS" if r is None else str(r.get("action"))
for c in [
  f"cp -t {H}/x.dat evil",            # T8 绝对形: 基线是否 hit?
  f'cp "-t{H}/tdir" x',               # T6 绝对形
  f"cp x -t {H}/",                    # -t home 绝对
  f"cp evil {H}/tdir/",               # 尾斜杠绝对
  f"cp -t {H}/tdir evil",             # -t 目录绝对分列
  f"install -t {H} src",              # install -t
]:
    print("%-52s -> %s" % (c[:52], call(c)))
# 视图出口法 T6 现形诊断
raw = '"-t~/.hermes/tdir"'
print("norm:", m._normalize_path(m._pair_unquote(raw), base=os.getcwd()))
print("view:", m._protect_view_norm(m._normalize_path(m._pair_unquote(raw), base=os.getcwd())))
