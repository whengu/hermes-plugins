# review-008-sec：write-guard round8 终审（安全路，只读）

- 评审人：sa-0（安全路）｜日期：2026-09-22｜基线：git 90de321 后 round8 修复版（handler.py 1173 行）
- 判据：reviews/round8-context.md + requirements/requirement-20260922-boundary.md。
  只在纳入范围 1-7 条内找新旁路；排除范围形态一律不立项（附录罗列）。
- 探针（本目录，全部落盘执行，命令行零载荷）：r8s_probe_a.py（重定向/输出参数/
  整词引号/链式续行）、r8s_probe_b.py（token 语义追踪/dd/exe 后缀/cmdlet/大小写）、
  r8s_probe_c.py（内嵌一层×常规写形态交叉、-t 族、execute_code os.system/subprocess）、
  r8s_probe_d.py（F-7-1/F-7-2 验收复测+红线）、r8s_probe_e.py（fd/& 重定向/wrapper/
  verbatim/FP 观察）。
- 基线复跑（实跑，非转述）：test_handler ALL PASS 29+4+250；_verify_r8 30/0、
  _verify_r7 30/0、_verify_r5 28/0、_verify_r3 25/0——与 fix-008 §6 记录一致，
  既有锁不回潮。

## 一、验收面结论（round8 修复项复测）

| 项 | 复测形 | 实测 | 判定 |
|---|---|---|---|
| F-7-1 | `cp evil `+bs+LF / bs+CRLF+守卫 handler | approve / approve | ✅封 |
| F-7-1 | `echo a`+2bs+LF+`cp evil GUARD` | approve | ✅盲替换误并旁路已闭 |
| F-7-1 | 双引号内 bs+LF、3bs/4bs、劈 token | PASS/PASS/approve/PASS | ✅与登记方向一致（奇偶族两形与 TC 形态不同但各自 POSIX 正确，见附录） |
| F-7-2 | `cp '--target-directory'=` / `"…"` + GUARD | approve / approve | ✅；workspace 负例 PASS |
| 红线 D | gateway bs+LF / bs+CRLF restart | block / block | ✅同源封堵 |

## 二、发现（纳入范围新旁路，全部实测复现）

<!--FINDINGS-->
