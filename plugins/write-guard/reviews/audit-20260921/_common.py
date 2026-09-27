"""对抗走查共用夹具：导入被测 handler，统一输出格式。"""
import os
import sys

BASE = r"d:\myagent\workspace\write-guard"
sys.path.insert(0, BASE)
import handler  # noqa: E402

CFG = r"D:\myagent\.hermes\config.yaml"
CFG_N = "d:/myagent/.hermes/config.yaml"
WG_PY = r"D:\myagent\.hermes\plugins\write-guard\handler.py"
WG_YAML = r"D:\myagent\.hermes\plugins\write-guard\plugin.yaml"


def verdict(res):
    if res is None:
        return "PASS"          # 放行
    return res.get("action", "?").upper()


def run(case_id, tool, args, expect, note=""):
    os.environ.pop("HERMES_HOME", None)
    try:
        res = handler.on_pre_tool_call(tool, args)
    except Exception as e:  # 入口直接抛异常（fail-open 兜底路径之外的崩溃）
        res = {"action": "CRASH:" + type(e).__name__}
    v = verdict(res)
    if expect == "?":
        ok = True
        mark = "INFO"
    else:
        ok = (v == expect)
        mark = "OK " if ok else "!! "
    msg = ""
    if isinstance(res, dict):
        msg = (res.get("message") or "")[:60].replace("\n", " ")
    print(f"{mark}{case_id:8s} {v:6s} (expect {expect:6s}) {tool:12s} {note} | {msg}")
    return ok
