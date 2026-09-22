import os
B = chr(92)
W = r"D:\myagent\workspace\write-guard"
src = open(W + B + "reviews" + B + "fix013-scratch" + B + "pm_verify_013.py", encoding="utf-8").read()
# correct textual replace of the *source* string that loads handler.py
needle = '"wg", W + B + "handler.py"'
assert needle in src, "needle missing"
src = src.replace(needle, '"wg", W + B + "_r2tmp" + B + "r13q" + B + "h_4e254c8.py"')
src = src.replace("sys.exit(1 if fails else 0)", "")
exec(compile(src, "pm013_on_round12_baseline", "exec"))
