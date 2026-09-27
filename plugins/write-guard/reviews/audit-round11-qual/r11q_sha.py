import hashlib, os
def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16] if os.path.isfile(p) else "MISSING"
src = "D:/myagent/workspace/write-guard"
dst = "D:/myagent/.hermes/plugins/write-guard"
files = ["__init__.py", "handler.py", "plugin.yaml"]
bad = []
print("== src vs main deploy ==")
for f in files:
    a, b = sha(f"{src}/{f}"), sha(f"{dst}/{f}")
    if a != b: bad.append(("main", f, a, b))
    print(("OK  " if a == b else "MISMATCH"), f, a, b)
print("== profile mirrors ==")
proot = "D:/myagent/.hermes/profiles"
for pd in sorted(os.listdir(proot)):
    t = f"{proot}/{pd}/plugins/write-guard"
    if os.path.isdir(t):
        for f in files:
            a, b = sha(f"{src}/{f}"), sha(f"{t}/{f}")
            if a != b: bad.append((pd, f, a, b))
            print(("OK  " if a == b else "MISMATCH"), pd, f, a, b)
print("BAD:", bad)
print("deploy-state: HEAD handler sha(src) =", sha(f"{src}/handler.py"))
