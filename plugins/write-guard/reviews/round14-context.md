# Round14 终审基线（context）

- **基线 git sha**: `8611f3c`（round14 修复闭环；round14a 代码 + round14b 收尾同批入库）
- **handler sha256 前 16**: `0a93ac9caf8ee25e`（主部署+双镜像，实测一致）
- **test_handler**: ALL PASS（29 scan + 4 hook + 363 new cases；TC-R14 16 条）
- **规格/制品**: reviews/fix-014-input.md / reviews/fix-014.md（五段全落 8×[DONE]）/
  reviews/fix014-scratch/pm_verify_014.py（27 形）/ _verify_r14.py（43 形）

## 改动摘要（三路合并：sec F-13-S1 + qual Q13-A/B + PM X-14-1）
- 改动A：`_pair_unquote` 接粘连入口全族四处匹配输入——`_GLUED_T_RE` /
  `--target-directory=` 前缀支 / `of=` 前缀支 / `_OUTPUT_FLAG_EQ_RE` 长形支；
  提取位点同步剥对引号视图（norm 链不动，F-7-2 不回潮）。T1~7/T15/T17 封堵。
- 改动B：`_OUTPUT_QUOTED_RE` 并 cluster 尾 o 支（单 dash 专属、`_OUTPUT_FLAG_CMDS_RE`
  门后）。T11~14 封堵、`"-oL"`/grep 门外/`"-H"` 零误拦锁保持。
- 改动C NOTES：fix-013.md 四节回填（Q13-C 补账）、Q13-D 第3/5次口径调和句、
  Q13-E 注释实名+幽灵 sha 修正、教训固化句（引号剥离类=全族粘连入口逐分支活证）。

## PM 门禁实测（终态复跑）
- pm_verify_014 27/0、_verify_r14 43/0、pm_verify_013 30/0 不回潮、
  test_handler 29+4+363 ALL PASS、九 verify 41/53/43/46/46/30/30/28/25 全 0、
  pm_verify_012 零 FAIL、红线六形正确（含 `cp "-t<PDIR>"` 缴械形=approve、
  `cp '-t<非保护>'`=PASS 零误拦）。
- **如实口径**：完成定义第 7 项端活证现场复跑被 approvals manual 审批卡超时拦截
  两次（收尾窗+PM 门禁窗，无人应答）——不重试不绕行，CHANGELOG 已登记；
  修复效果以双翻转表+回退表背书，真写可运行性沿用立项前活证链（ecca470）。

## 收敛进度
round13 安全路改动A/B 本体零缺陷获双路确认；本批修的是三代既有组合面残留。
若 round14 双路均 PASS → 满足收敛判据（纳入范围零缺陷+排除项全登记），进入
gateway 重启（需用户在场批准确认插件热生效）+ 终版审查链报告收尾。
