# -*- coding: utf-8 -*-
"""fix-008 test_handler.py 编辑器：新增 run_r8_fixes 并注册调用。"""
import io

P = "D:/myagent/workspace/write-guard/test_handler.py"
NL, CR = chr(10), chr(13)
src = io.open(P, encoding="utf-8", newline="").read()
CRLF = (CR + NL) in src
EOL = CR + NL if CRLF else NL

FUNC = (
    'def run_r8_fixes():' + EOL +
    '    """round8 最小化修复回归（F-7-1 续行归一语义重写 + F-7-2 灰区 + 接受边界锁）。"""' + EOL +
    '    NL, CR, BS, SQ, DQ = chr(10), chr(13), chr(92), chr(39), chr(34)' + EOL +
    '    GUARD = "D:/myagent/.hermes/plugins/write-guard"' + EOL +
    '    # F-7-1（必修）：真续行两形必须封堵——删除式粘连后行直接相接（approve）' + EOL +
    '    res = _call("terminal", {"command": "cp evil " + BS + NL + GUARD})' + EOL +
    '    _rec("TC-R8-01 真续行 bs+LF 粘连 cp 守卫目录 → approve（F-7-1）", _is_approve(res))' + EOL +
    '    res = _call("terminal", {"command": "cp evil " + BS + CR + NL + GUARD})' + EOL +
    '    _rec("TC-R8-02 真续行 bs+CRLF 粘连 cp 守卫目录 → approve（F-7-1）", _is_approve(res))' + EOL +
    '    # 成对反斜杠+真换行：粘连不吞转义对，换行仍是分隔符（盲 replace 旧形=旁路，修后拦）' + EOL +
    '    res = _call("terminal", {"command": "echo a" + BS + BS + NL + "cp evil " + GUARD})' + EOL +
    '    _rec("TC-R8-03 2bs+LF 分段后 cp 守卫目录 → approve（奇偶成对消耗）", _is_approve(res))' + EOL +
    '    # 双引号内 bs+LF：引号内不处理（2026-09-22 范围决策排除第 2 条）——锁现状 PASS' + EOL +
    '    res = _call("terminal", {"command": "echo " + DQ + "a" + BS + NL + GUARD + DQ})' + EOL +
    '    _rec("TC-R8-04 双引号内 bs+LF 登记形 → 锁现状放行（排除范围2）", res is None)' + EOL +
    '    res = _call("terminal", {"command": "echo " + SQ + "a" + BS + NL + "cp evil " + GUARD + SQ})' + EOL +
    '    _rec("TC-R8-05 单引号内 bs+LF 字面不误伤 → 放行", res is None)' + EOL +
    '    # 奇偶族余项锁现状（登记见 CHANGELOG 接受边界）：3bs=粘连方向 approve；4bs=分段 PASS' + EOL +
    '    res = _call("terminal", {"command": "cp evil " + BS * 3 + NL + GUARD})' + EOL +
    '    _rec("TC-R8-06 3bs+LF → approve（粘连已发生未裂段，登记族锁向）", _is_approve(res))' + EOL +
    '    res = _call("terminal", {"command": "cp evil " + BS * 4 + NL + GUARD})' + EOL +
    '    _rec("TC-R8-07 4bs+LF → 放行（POSIX 转义对+独立换行，登记族锁向）", res is None)' + EOL +
    '    # 引号穿插劈 token 形（排除范围第 1 条）：锁现状 PASS，防日后误扩' + EOL +
    '    res = _call("terminal", {"command": "cp -" + SQ + "t" + SQ + GUARD + " evil"})' + EOL +
    '    _rec("TC-R8-08 穿插 cp -\'t\'GUARD → 锁现状放行（排除范围1）", res is None)' + EOL +
    '    # F-7-2（处置=修）：引号长选项词后 = 粘连两形 approve；workspace 负例放行' + EOL +
    '    res = _call("terminal", {"command": "cp " + SQ + "--target-directory" + SQ + "=" + GUARD + " x"})' + EOL +
    '    _rec("TC-R8-09 cp \'--target-directory\'=GUARD → approve（F-7-2）", _is_approve(res))' + EOL +
    '    res = _call("terminal", {"command": "cp " + DQ + "--target-directory" + DQ + "=" + GUARD + " x"})' + EOL +
    '    _rec("TC-R8-10 cp \"--target-directory\"=GUARD → approve（F-7-2 双引号形）", _is_approve(res))' + EOL +
    '    res = _call("terminal", {"command": "cp " + SQ + "--target-directory" + SQ + "=" + "D:/myagent/workspace/out" + " x"})' + EOL +
    '    _rec("TC-R8-11 F-7-2 非 home 目标 → 放行（负例）", res is None)' + EOL +
    '    # 整词包裹在纳入范围（OOB 2026-09-22 口径）：引号包路径必须仍 approve' + EOL +
    '    res = _call("terminal", {"command": "cp evil " + SQ + GUARD + SQ})' + EOL +
    '    _rec("TC-R8-12 整词单引号包守卫路径 → approve（纳入范围3锁）", _is_approve(res))' + EOL +
    '    res = _call("terminal", {"command": "cp evil " + DQ + GUARD + DQ})' + EOL +
    '    _rec("TC-R8-13 整词双引号包守卫路径 → approve（纳入范围3锁）", _is_approve(res))' + EOL +
    '    # 红线：gateway 禁令续行两形 block 保持' + EOL +
    '    res = _call("terminal", {"command": "hermes gateway " + BS + NL + "restart"})' + EOL +
    '    _rec("TC-R8-14 gateway bs+LF restart → block（红线保持）", _is_block(res))' + EOL +
    '    res = _call("terminal", {"command": "hermes gateway " + BS + CR + NL + "restart"})' + EOL +
    '    _rec("TC-R8-15 gateway bs+CRLF restart → block（同源封堵）", _is_block(res))' + EOL +
    '    # 回归负例零回潮：读 cat / workspace 写' + EOL +
    '    res = _call("terminal", {"command": "cat " + GUARD + "/handler.py"})' + EOL +
    '    _rec("TC-R8-16 cat 守卫文件 → 放行（负例回潮哨）", res is None)' + EOL +
    '    res = _call("terminal", {"command": "echo x > D:/myagent/workspace/a.txt"})' + EOL +
    '    _rec("TC-R8-17 workspace 写 → 放行（负例回潮哨）", res is None)' + EOL +
    EOL + EOL
)

anchor_call = "run_r7_fixes()" + EOL
assert src.count(anchor_call) == 1
src = src.replace(anchor_call, anchor_call + "run_r8_fixes()" + EOL)
anchor_def = "def run_scheduler():" + EOL
assert src.count(anchor_def) == 1
src = src.replace(anchor_def, FUNC + anchor_def)

io.open(P, "w", encoding="utf-8", newline="").write(src)
print("test_handler.py patched (CRLF=%s)" % CRLF)
