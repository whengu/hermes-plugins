# Round15 终审基线（context）

- **基线 git sha**: `307e5cd`（round15 修复闭环）
- **test_handler**: ALL PASS（29 + 4 + 369；TC-R15 6 条）
- **改动**：1 字符正则收窄 `_OUTPUT_QUOTED_RE` 第三支 `[-]?`→`[-]`（S14-1/Q1 双路同根
  零 dash 误拦）+ NOTES（Q2 curl `--output=` 机理句改实 rc=2 不可运行形、教训句
  「正则可选项与注释承诺逐词对拍」、旧口径修正）。
- **PM 六项门禁独立复跑全绿**：pm014 29/0（T19/T20 新靶心转 PASS）、test 369 ALL PASS、
  _verify_r14 43/0、pm013 30/0、pm012 零 FAIL、红线四形 + FP 双验（Cairo/logo=PASS、
  -so/-O/E1/-oL 锁全对）。
- **round14 裁决链**：sec CHANGES REQ（S14-1 1 MED，本批修）+ qual PASS_WITH_NOTES
  （Q1 同根已修、Q2 机理句已改实、Q3/Q4/Q5 随批）。

## 收敛进度判断
round14 质量路已给 PASS_WITH_NOTES（阻断 0，六类粘连入口逐支活证闭环）；本批修掉安全路
唯一 MED。若 round15 双路均无纳入范围 finding → 满足收敛判据（纳入范围零缺陷+排除项
全登记），目标达成。

## 复审聚焦建议
本轮改动面极小（2 行），复审不必重扫全历史面；重点：①该字符收窄有无第三维邻域副作用
（`"-"` 纯 dash、`"--"` 形、`"-" + o` 组合）；②NOTES 三处名实对拍；③门禁链零回退复跑。
