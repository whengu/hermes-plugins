# round12 终审基线（2026-09-23 00:4x）

被审对象：workspace/write-guard（git round12 提交）+ 部署同代际。
准绳不变：requirements/requirement-20260922-boundary.md。

## 本轮改动（fix-012，规格 reviews/fix-012-input.md，制品 reviews/fix-012.md 七段 [DONE]）
1. _PS_NAMED_TARGET_RE 收窄 Destination|FilePath（F-11-3/Q-11-1 源参误绑修复，ANY 五词不动）
2. _GLUED_NAMED_RE 冒号粘连 `-Destination:<值>`（含引号值）提取进命名支（F-11-1）
3. _OUTPUT_QUOTED_RE 引号包选项词 `curl "-o" <CFG>`（内容不可选，PM 修正提案缺陷，F-11-2）
4. _OUTPUT_FLAG_RE 并 dash cluster 尾 o 支 `-{1,2}[a-zA-Z]*o`（斜杠/数字不参与，F-11-4）
+ NOTES：fix-011 §0 [DONE]、TC-R11 笔误一处如实登记。TC-R12 20 条；_verify_r12 53 项。

## 验收基线（PM 独立复跑背书）
test_handler ALL PASS 29+4+329；_verify_r12 53/0、r11 43/0、r10 46/0、r9 46/0、r8 30/0、
r7 30/0、r5 28/0、r3 25/0；pm_verify_012 23 形全达期望；pm_verify_011 十六行零回退；
红线四形（on_pre_tool_call）：gateway block、cp 配置弹卡、Copy-Item 源位 PASS、rm -r 分层；
处置分流：冒号粘连写配置=approve 弹卡、curl -o 族写守卫源码=block。

## 收敛判据（不变）
- 立项仅限：纳入范围内新旁路 / 纳入范围内误拦 / 名实不符。
- 排除范围形态与全部已登记边界（含本轮 a4 等号形附录、缩写别名族等 round11 附录 7 族）
  → 一律附录不立项。
- 双路均 PASS/PASS_WITH_NOTES（NOTES 不涉 handler 逻辑）→ 整体收敛 →
  gateway 重启 + 终版审查链报告。

## 复审提示
- 探针入口 on_pre_tool_call（四守卫全链）。
- 本轮四改动全在选项词识别/提取层，重点回归面：引号形态家族（""/''/整词/粘连交叉）、
  cluster 族（-sSLfo/-qO/-ro 与新支的邻域如 --http1.0、-o= 等号形、-O 大写红线向）、
  PS 命名支三向（前置封堵/源位放行/双标志否决）与冒号形交叉（`-Destination:"-x"` 值含 dash）。
- 前四轮规律：每轮修复引入 1-2 条新回归——请对 diff 的每条 or 支做双向（封堵+误拦）差分。
