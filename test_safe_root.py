"""测试 HERMES_WRITE_SAFE_ROOT 是否支持整盘（D:/F:）白名单。

只读测试：仅设置子进程环境变量，调用 Hermes 真实的 file_safety 判定函数，
不做任何磁盘写入。
"""

import importlib.util
import os
import sys

REPO = r"D:\Project\guwh\hermes-agent"
sys.path.insert(0, REPO)
# 模拟真实运行时的 HERMES_HOME（影响 state.db/.env/sessions 等受保护路径判定）
os.environ["HERMES_HOME"] = r"D:\myagent\.hermes"

spec = importlib.util.spec_from_file_location(
    "file_safety", os.path.join(REPO, "agent", "file_safety.py")
)
assert spec is not None and spec.loader is not None
file_safety = importlib.util.module_from_spec(spec)
spec.loader.exec_module(file_safety)

CANDIDATES = [
    ("A: D:\\;F:\\  （盘符+反斜杠）", "D:\\;F:\\"),
    ("B: D:;F:      （裸盘符）", "D:;F:"),
    ("C: D:/;F:/    （盘符+正斜杠）", "D:/;F:/"),
]

PROBES = [
    (r"D:\workspace\a.txt", "D盘普通路径"),
    (r"D:\a.txt", "D盘根下直接文件"),
    ("D:\\", "D盘根目录本身"),
    (r"F:\x\y.txt", "F盘普通路径"),
    (r"C:\Users\guwh\x.txt", "C盘用户目录"),
    (r"C:\Windows\Temp\x.txt", "C盘系统Temp"),
    (r"E:\elsewhere.txt", "E盘（未列入白名单）"),
    (r"D:\myagent\.hermes\.env", "Hermes .env（凭据文件，应仍被拒）"),
    (r"D:\myagent\.hermes\state.db", "Hermes state.db（会话库，应仍被拒）"),
    (r"D:\myagent\.hermes\auth.json", "Hermes auth.json（凭据，应仍被拒）"),
]

for label, val in CANDIDATES:
    os.environ["HERMES_WRITE_SAFE_ROOT"] = val
    print("=" * 64)
    print("配置值:", label)
    print("解析后的 roots:", sorted(file_safety.get_safe_write_roots()))
    for p, desc in PROBES:
        denied = file_safety.is_write_denied(p)
        mark = "拒绝" if denied else "允许"
        print(f"  [{mark}] {p:<38} ({desc})")
    print()
