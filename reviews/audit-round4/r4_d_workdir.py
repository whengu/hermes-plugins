# -*- coding: utf-8 -*-
"""第四批定向：C-1 修复的纵深——workdir 未绝对化（相对/混排形态）→ A 面基准落差复确。"""
import importlib.util, os
spec = importlib.util.spec_from_file_location("wg4d", "handler.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
os.environ["HERMES_HOME"] = r"D:\myagent\.hermes"
os.chdir("D:\\myagent\\workspace")   # 模拟进程 cwd=workspace（平台默认）
S=chr(92); HOME="D:"+S+"myagent"+S+".hermes"; CFG=HOME+S+"config.yaml"
def act(t,a):
    r=h.on_pre_tool_call(t,a); return (r or {}).get("action") or "PASS"
def T(c,**kw): return act("terminal",{"command":c,**kw})
P=lambda tag,g: print("  %-56s -> %s"%(tag,g))
print("== workdir 绝对化缺失（平台 _resolve_command_cwd: abspath(expanduser(workdir))）==")
P("workdir='..\\\\.hermes' + 相对重定向（平台真实落盘=home）", T("echo hi > config.yaml", workdir=".."+S+".hermes"))
P("workdir='../.hermes' 正斜杠", T("echo hi > config.yaml", workdir="../.hermes"))
P("workdir='..\\\\.hermes' + 相对 cp（approve 面）", T("cp k.yaml settings.json", workdir=".."+S+".hermes"))
P("workdir='D:\\\\myagent\\\\workspace\\\\..\\\\.hermes' 含..段绝对", T("echo hi > config.yaml", workdir="D:"+S+"myagent"+S+"workspace"+S+".."+S+".hermes"))
P("workdir='~\\\\..\\\\myagent\\\\.hermes'（expanduser 平台生效）", T("echo hi > config.yaml", workdir="~"+S+"x"))
P("对照绝对 workdir（round3 修复形态）", T("echo hi > config.yaml", workdir=HOME))
print("== C 面 workdir 相对指 tmp ==")
P("workdir='..\\\\..\\\\tmp' (平台真实 cd 到盘根 tmp)", T("touch ok", workdir=".."+S+".."+S+"tmp"))
P("workdir 绝对 D:"+S+"tmp (round3 修复形态)", T("touch ok", workdir="D:"+S+"tmp"))
print("== 附带：内嵌递归基准同为未绝对化 workdir ==")
P("bash -c + 相对 workdir", T("bash -c \"echo x > config.yaml\"", workdir=".."+S+".hermes"))
