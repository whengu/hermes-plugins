
import importlib.util, sys
spec = importlib.util.spec_from_file_location("handler", "handler.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
HOME = h._hermes_home()
CFG  = HOME + "/config.yaml"
WS   = "D:/myagent/workspace/a.txt"
GD   = HOME + "/plugins/write-guard"
def act(cmd):
    r = h.on_pre_tool_call("terminal", {"command": cmd})
    if r is None: return "PASS"
    return r.get("action","?")
cases = [
 ("cp src CFG 末位目标弹卡", f"cp {WS} {CFG}", "approve"),
 ("cp CFG dst 源位读", f"cp {CFG} {WS}", "PASS"),
 ("cp -t HOME src", f"cp {WS} -t {HOME}", "approve"),
 ("cp -rt 簇", f"cp -rt {WS} {HOME}", "approve"),
 ("install -t", f"install -t {HOME} {WS}", "approve"),
 ("rsync -t CFG dst 纯读向(R4-1)", f"rsync -t {CFG} {WS}", "PASS"),
 ("rsync src CFG 末位", f"rsync {WS} {CFG}", "approve"),
 ("robocopy 三参形不受影响", f"robocopy D:/src {CFG} f.txt", None),
 ("cmd copy /Y 末位 CFG", f"copy /Y {WS} {CFG}", "approve"),
 ("cmd copy CFG dst", f"copy {CFG} {WS}", "PASS"),
 ("Copy-Item src dst 无标志末位仍拦", f"Copy-Item {WS} {CFG}", "approve"),
 ("Copy-Item -Path CFG -Destination 非保护", f"Copy-Item -Path {CFG} -Destination {WS}", "PASS"),
 ("sort /O CFG d.txt", f"sort /O {CFG} d.txt", "block"),
 ("sort /o CFG d.txt", f"sort /o {CFG} d.txt", "block"),
 ("curl -o CFG", f"curl -o {CFG} http://x", "block"),
 ("curl http://x/o CFG 归正", f"curl http://x/o {CFG}", "PASS"),
 ("Tee-Object -FilePath CFG", f"Tee-Object -InputObject x -FilePath {CFG}", "approve"),
 ("Set-Content CFG", f"Set-Content {CFG} hi", "block"),
 ("Out-File CFG", f"somecmd | Out-File {CFG}", "block"),
 ("grep -o CFG 未知命令面放行", f"grep -o {CFG} f", "PASS"),
 ("sed -i CFG", f"sed -i s/a/b/ {CFG}", "approve"),
 ("cp -t粘连", f"cp -t{HOME} {WS}", "approve"),
 ("mv src CFG", f"mv {WS} {CFG}", "approve"),
 ("Copy-Item -LiteralPath CFG -Destination 非保护", f"Copy-Item -LiteralPath {CFG} -Destination {WS}", "PASS"),
 ("pwsh载体 反向 -Destination 非保护 CFG", f'pwsh -Command "Copy-Item -Destination {WS} {CFG}"', "PASS"),
 ("pwsh载体 正向 -Destination CFG 非保护", f'pwsh -Command "Copy-Item -Destination {CFG} {WS}"', "approve"),
 ("cp -t HOME 与 PS 命名交叉 copy -t", f"copy -t {HOME} {WS}", None),
]
bad = []
for name, cmd, want in cases:
    got = act(cmd)
    ok = (want is None) or (got == want)
    if not ok: bad.append((name,got,want))
    print(("ok  " if ok else "MISMATCH ")+f"{name:46s} got={got:8s} want={want}")
print("BAD:", bad)
