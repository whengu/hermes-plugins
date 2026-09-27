# round10 安全路探针 0：部署一致性只读核对（源 vs 主部署 vs 双镜像 sha256/16）
import hashlib, os

def sha(p):
    try:
        return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
    except Exception:
        return "MISSING"

base = r"D:\myagent"
targets = {
    "workspace源": r"workspace\write-guard",
    "主部署": r".hermes\plugins\write-guard",
    "镜像architect": r".hermes\profiles\architect\plugins\write-guard",
    "镜像developer": r".hermes\profiles\developer\plugins\write-guard",
}
files = ["__init__.py", "handler.py", "plugin.yaml"]
rows = {}
for name, rel in targets.items():
    rows[name] = {f: sha(os.path.join(base, rel, f)) for f in files}
for f in files:
    vals = {n: r[f] for n, r in rows.items()}
    same = len(set(vals.values())) == 1
    print(f, "同代际" if same else "分叉", vals)
