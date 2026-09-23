# round16 门禁链：全 verify 代跑（零回退核对）
import subprocess, sys, os
B = chr(92)
W = r"D:\myagent\workspace\write-guard"
scripts = [
    "_verify_r3.py", "_verify_r5.py", "_verify_r7.py", "_verify_r8.py",
    "_verify_r9.py", "_verify_r10.py", "_verify_r11.py", "_verify_r12.py",
    "_verify_r13.py", "_verify_r14.py",
    "reviews" + B + "fix012-scratch" + B + "pm_verify_012.py",
    "reviews" + B + "fix013-scratch" + B + "pm_verify_013.py",
    "reviews" + B + "fix014-scratch" + B + "pm_verify_014.py",
    "reviews" + B + "fix016-scratch" + B + "pm_verify_016.py",
]
for s in scripts:
    p = os.path.join(W, s)
    r = subprocess.run([sys.executable, p], capture_output=True, text=True, timeout=120)
    out = (r.stdout or "").replace("\r\n", "\n").strip().split("\n")
    tail = out[-1] if out else "?"
    fail_lines = [l for l in out if l.startswith("FAIL")]
    print(f"== {s:46s} rc={r.returncode} :: {tail}")
    for fl in fail_lines[:6]:
        print("   ", fl)
