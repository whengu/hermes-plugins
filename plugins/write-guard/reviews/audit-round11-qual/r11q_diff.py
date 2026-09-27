
import importlib.util
def load(p,n):
    spec = importlib.util.spec_from_file_location(n,p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
old = load("reviews/audit-round10-qual/base/handler_r10commit.py","old_h")
new = load("handler.py","new_h")
HOME = new._hermes_home(); CFG = HOME+"/config.yaml"; WS="D:/myagent/workspace/a.txt"
def act(h,cmd):
    r = h.on_pre_tool_call("terminal", {"command": cmd})
    return "PASS" if r is None else r.get("action","?")
cmds = [
 f"sed -i s/a/b/ {CFG}",
 f"mv {WS} {CFG}",
 f"cp {WS} {CFG}", f"cp {CFG} {WS}",
 f"cp {WS} -t {HOME}", f"cp -rt {WS} {HOME}", f"install -t {HOME} {WS}",
 f"rsync -t {CFG} {WS}", f"rsync {WS} {CFG}",
 f"robocopy D:/src {CFG} f.txt",
 f"copy /Y {WS} {CFG}", f"copy {CFG} {WS}",
 f"Copy-Item {WS} {CFG}",
 f"Copy-Item -Path {CFG} -Destination {WS}",
 f"sort /O {CFG} d.txt", f"sort /o {CFG} d.txt", f"curl -o {CFG} http://x",
 f"curl http://x/o {CFG}",
 f"Tee-Object -InputObject x -FilePath {CFG}",
 f"Set-Content {CFG} hi", f"somecmd | Out-File {CFG}",
 f"grep -o {CFG} f", f"cp -t{HOME} {WS}",
 f"Copy-Item -LiteralPath {CFG} -Destination {WS}",
 f'pwsh -Command "Copy-Item -Destination {WS} {CFG}"',
 f'pwsh -Command "Copy-Item -Destination {CFG} {WS}"',
 f"copy -t {HOME} {WS}",
 f"sort D:/myagent/workspace/o {CFG}",
 f"sort D:/myagent/workspace/my-dir-o {CFG}",
]
diff=[]
for c in cmds:
    o,n = act(old,c), act(new,c)
    flag = "SAME" if o==n else "DIFF"
    if o!=n: diff.append((c,o,n))
    print(f"{flag:4s} old={o:8s} new={n:8s}  {c[:70]}")
print("DIFFS:", len(diff))
for d in diff: print(d)
