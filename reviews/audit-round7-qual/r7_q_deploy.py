# 部署一致性精确比对：git 基线 handler.py vs 主部署/双镜像（忽略行尾差异，报告真实内容差）
import difflib, io, subprocess, os

p = subprocess.run("git show 90de321:handler.py", shell=True, capture_output=True)
base = p.stdout.decode("utf-8", "replace")
targets = {
    "main": r"D:/myagent/.hermes/plugins/write-guard/handler.py",
    "mirror-arch": r"D:/myagent/.hermes/profiles/architect/plugins/write-guard/handler.py",
    "mirror-dev": r"D:/myagent/.hermes/profiles/developer/plugins/write-guard/handler.py",
}
for tag, path in targets.items():
    if not os.path.exists(path):
        print(tag, "MISSING")
        continue
    cur = io.open(path, encoding="utf-8", newline="").read().replace("\r\n", "\n")
    b = base.replace("\r\n", "\n")
    if cur == b:
        print(tag, "IDENTICAL（行尾归一后逐行相同）")
        continue
    dl = list(difflib.unified_diff(b.splitlines(), cur.splitlines(), lineterm="", n=1))
    print(tag, "DIFFERS, diff-lines:", len(dl))
    for l in dl[:12]:
        print("   ", l[:110])
