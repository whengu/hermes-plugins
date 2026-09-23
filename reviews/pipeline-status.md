# write-guard 流水线状态（PM 维护，2026-09-22 15:5x）

阶段模型（dev-pipeline）：REVIEW 发现 → FIX（修复 subagent，按 fix-NNN.md 输入）
→ 门禁验证（PM 实跑测试+部署一致）→ RE-REVIEW → 循环至双路 PASS。

## 历史轮次（注：round2~round7 的 FIX 由 PM 亲自执行，违反角色分离，已纠正——
## 自 round8 起修复一律派修复 subagent，PM 只写 fix 输入文档 + 门禁验证）

| 轮 | 复审结论 | 修复 commit | 基线 |
|---|---|---|---|
| round2 | 双路 CR | 5d93150/559b050/1d5adf9 | 176 用例 |
| round3 | 双路 CR | 69aafcf | 192 用例 |
| round4 | 双路 CR | 4d08ddd | 208 用例 |
| round5 | sa-1 轻量CR；sa-0 截断(转写捞实锤) | 8fa3fe1 | 219 用例 |
| round6 | 双路 CR（NL 换行 HIGH + Q-6-1） | 90de321 | 233 用例 |
| round7 | **双路 CR 已收齐**：sa-1 F-7-1(HIGH,PM 复验实锤)/F-7-2 MED/F-7-3,4 登记；sa-0 截断但转写实测（引号 cluster、POSIX 奇偶真值、半混长形）全部并入 fix-008-input.md | a0dab67（round8 提交） | 250 用例（修后） |
| round8 | 双路终审：质量 PASS_WITH_NOTES（N1~N5 文档级已处置，be14c7f）；安全 CHANGES REQUIRED（纳入范围 S-1~S-5，PM 实测复现）→ 进 round9 | a0dab67/be14c7f | 250→277 |
| round9 | FIX（sa-0-500024c2，交卷 completed 未截断）+PM 八项门禁全绿→commit cbd6301+deploy。双路终审：质量 PASS_WITH_NOTES（Q9-N1~N5）；安全 CHANGES REQUIRED（F-9-1 复制族源位误拦/F-9-2 wrapper x 载体/F-9-3 sort /O/F-9-4 tee 非末位）→ 进 round10 | cbd6301 | 277 |
| round10 | FIX（sa-0-8efcf7dd，交卷截断第 6 次制品零损失）+PM 门禁→commit 2cc28cf+deploy。双路 CR：F-10-1/Q10-1 命名目标前置双向、F-10-2/Q10-3 /o 外溢（同根互证）+Q10-2/4 NOTES → round11 | 2cc28cf | 292 |
| round11 | FIX（sa-0-40874a2a 完整交付未截断）+PM 门禁全绿→commit 94998f5+deploy。双路 CR：F-11-3/Q-11-1 绑定词含源参（PM 规格清单根因）/F-11-1 冒号粘连/F-11-2 引号选项词/F-11-4 cluster 尾o（活证背书）→ round12 | 94998f5 | 309 |
| round12 | FIX（sa-0-4298d00b 完整交付，steer 骨架纠偏 1 次）+PM 门禁全绿（11 verify+pm012 23 形翻转+pm011 16 行零回退+红线四形 on_pre_tool_call+分流语义）→commit 4e254c8+deploy。双路终审在途（deleg_aadc7cca sec / deleg_be807b34 qual）| 4e254c8 | 329 |

## 门禁基线（PM 验证过的事实，2026-09-22）
- git HEAD 90de321，工作区干净
- test_handler.py ALL PASS（29 scan + 4 hook + 233 new）
- _verify_r3 25/0、_verify_r5 28/0、_verify_r7 30/0
- 部署一致：主部署 + profiles/{architect,developer} 镜像（deploy.py 校验）
- 红线不变：approvals.mode=manual、rm -r 保持拦截、改名/复制不拦、cp 写配置弹卡、
  force-push/sudo 永不白名单、不加复杂度

## 下一步
1. 等 round7 双路结果（报告落 reviews/audit-round7-{sec,qual}/review-007-*.md）
2. 若有 finding → PM 写 reviews/fix-008.md（findings+证据+修法建议+红线+验收标准）
   → 派修复 subagent（goal 短小指向文档）→ PM 实跑门禁 → 派 round8 复审
3. 双路 PASS → 流水线收尾：处理 gateway 重启（补丁生效）、清临时脚本、终报


---
## Round13（2026-09-23）— 修复闭环 + 在途复审
- 施工子代理 sa-0-59555a31 交卷截断（第 7 次），制品先落盘纪律生效：代码+TC-R13 18 条+
  CHANGELOG round13 节在盘（fix-013.md 仅 §0 落，§A/§B/§N/§V 未回填——Q13-C 修正令改实）。
- 改动：A per-cmd 目标表（F-12-1/2）+ B 引号粘连选项值（F-12-3）。Z1/Z3 双绑必败形按
  PM pwsh 活证锁 PASS（语义正确零写，禁特判——规格补丁 a5ee7de）。
- 门禁 12 项全绿（pm_verify_013 30/30、九 verify 零失败、pm_verify_012 23 形零回退、红线四形）。
- **git 10a2094 / 部署+双镜像 sha cf61f3291970a021（实测一致）**；test 29+4+347。
- 教训固化入 CHANGELOG：修复引入回归第 3 次，三次同构（词表收窄压平一维语义）；固化规则
  =词表类修复验收必含 per-cmd 活证，禁只跑翻转表。
- 在途：round13 双路复审（安全+质量），基线 10a2094。


---
## Round14（2026-09-23）— 修复闭环 + 双路复审（sec 1 MED / qual PASS_WITH_NOTES）
- 三路合并立项（sec F-13-S1 + qual Q13-A/B + PM X-14-1）：粘连入口引号整包全族封堵。
- round14a 施工截断（第 8 次）但代码面完整；round14b 收尾批补齐制品五段+TC 16+_verify_r14。
- 端活证第 7 项两次审批超时未现场复跑——CHANGELOG 如实登记，不据旧证扩称新测。
- **git 8611f3c / 部署四镜像 0a93ac9caf8ee25e**；test 29+4+363。
- 复审：sec CHANGES REQ（S14-1 MED：cluster `[-]?` 零 dash 放行致 "Cairo"/"logo" 误拦）
  + qual PASS_WITH_NOTES（Q1 同根、Q2 死选项机理句失实——我方 round14 CHANGELOG 再犯，
  第六次名实不实现象；六类粘连入口逐支活证闭环）。PM wave3 挖洞 14 形零异常。

## Round15（2026-09-23）— 1 字符修复闭环 + 在途合并终审
- S14-1/Q1 同根修复：`_OUTPUT_QUOTED_RE` 第三支 `[-]?`→`[-]`（PM 猴补丁定演 11 形后派单，
  施工子代理未截断交付——制品纪律 8 轮后首次全程无截断）。
- NOTES：Q2 机理句改实（curl `--output=` 端 rc=2 不可运行形归 curl 域；「=并入文件名」
  归 cluster 短形专属）+ 教训句「正则可选项与注释承诺逐词对拍」+ TC-R15 6 条。
- PM 六项门禁独立复跑全绿：pm014 29/0、test 29+4+369、r14 43/0、pm013 30/0、pm012 零 FAIL、
  红线四形+FP 双验。**git 307e5cd，部署四镜像一致**。
- 在途：round15 合并终审（改动面 2 行，聚焦邻域差分/名实对拍/门禁复跑；双路重扫违
  "不加复杂度"边界）。**若 PASS → 满足收敛判据（纳入范围零缺陷+排除项全登记），
  目标达成，转 gateway 重启（待用户在会话时批审批卡）+ 终版审查链报告。**


---
## Round15（2026-09-23）— 合并终审 PASS · 收敛判据达成 ✅
- 改动面 2 行（正则 `[-]?`→`[-]` + 注释对拍）。施工子代理未截断交付（8 轮截断后首次全程
  干净），PM 六项门禁独立复跑全绿后 commit 307e5cd + deploy（四镜像 `149497733ab9e8c2` 一致）。
- 合并终审（sa-0-867c9b65，改动面极小故聚焦复审不双路全量重扫，违"不加复杂度"边界）：
  **PASS** —— 双代差分 53 形切换集仅 6 形且全为"误拦→放行"方向、32 形零旁路逃逸；
  名实三方逐词一致；Q2 机理端活证独立重跑坐实；九项门禁全绿。
- NOTES 收线两条（N-15-1 sha 算法注 / N-15-2 `"-so "` 尾随空白死形入接受边界）——PM 实测
  背书入 CHANGELOG round15 节。PM wave4 邻域探针 16 形零异常（6b4974e）。
- **收敛判定：纳入范围内零缺陷 + 排除项全部登记在案 = 达成。** 自 round15 基线（git
  HEAD 终态）起审查循环终止。剩余唯一收尾= gateway 重启使 round3~15 全部补丁在运行进程
  生效（approvals.mode: manual 下 `hermes gateway restart` 被守卫正确拦截，需用户在会话
  时批准审批卡或手动重启——守卫按设计工作，此为红线非缺陷）。


---
## Round16（2026-09-23）— 用户提议触发：tilde/$HOME 别名路径写旁路立项
- 用户提议「审批加 ~/.hermes/ 路径检查，或干脆 */.hermes/*.yaml」。PM 实测坐实真旁路
  （cp/echo>/sed -i/-t 粘连/-o 粘连/tee $HOME/旧符号链接别名绝对形/目标位 mv 共 9 形
  judge=PASS，绝对路径同语义=approve；读位 cat/mv 源位 正常 PASS）。
- 设计决策：不采裸 glob 字面匹配（读位误拦+漏 .py/memories 面），采 **.hermes 段锚定
  归一**——写目标判定输入处取 .hermes 后 rel 与既有受保护集合 rel 级比对，单点插入
  ≤12 行逻辑插入。【r17 改实：「读/写位置语义全继承」失实——仅接两函数入口，宽拦族
  比较点未接=F-16-S1，round17 补齐（第七次名实登记）。】
- 完成定义 pm_verify_016 基线 7 ok/9 FAIL → 0 FAIL。立项 commit 4ddc3ba。
- 在途：sa-0-56a8f57e 照图施工（制品纪律+TC-R16+CHANGELOG 随批）。


### Round16 施工交付与 PM 收线（2026-09-23）
- sa-0-56a8f57e 交付截断（第 9 次），制品 6×[DONE]+代码+TC 全落盘；CHANGELOG round16 节
  为截断缺口，PM 按亲验数字收线补记（含 diff 行数失实一处自纠 +31→+30 增）。
- PM 门禁全亲验：pm016 16/16（9 靶心转绿+7 锁零回退）、test 29+4+381、r14 43、pm014 29、
  pm013 30、九 verify 全 0、pm012 零 FAIL、红线四形 4/4、tilde 抽验 7 形零误拦。
- 用户确认项：cat 读必须放过=已锁 K1/K7 反例（弹卡即验收失败）。
- 在途：round16 聚焦复审（改动面 ~30 行单点归一+mv 甄别，邻域差分+读写位置语义专项）。


---
## Round17（2026-09-23）— F-16-S1 宽拦族 tilde 封堵 + 审批文案自解释（用户「可解释」裁决并批）
- 施工子代理 sa-0-c88dd1fb 全程未截断交付：改动1/2+TC-R17 13 条+pm017 19/0+全链门禁
  实跑；其红线复验内联命令被审批卡拒后按纪律停手报告（正确行为），PM 收线窗代跑第 4 项。
- PM 独立复验完成定义 5 项全绿：pm017 19/0（含 M1/M2 文案锁）、pm016 16、pm014 29、
  pm013 30、r14 43、九 verify 全 0、pm012 零 FAIL、test 29+4+394 ALL PASS、红线四形
  4/4、两跳端到端判定层复验（入口断链+改名红线维持+范围可解释）。diff 逐行亲读：
  视图仅接比较点，绝对形 norm==视图恒零漂移，wide_landing 系文案信号判定零变化。
- NOTES 收线：N-16-1 在册点名、N-16-2 勾齐、N-16-3 口径、round16「全族继承」三处失实句
  就地改实（第七次名实登记：把设计意图写成已达成事实→新规句式=宣称继承/覆盖必须列接点清单）。
- 在途：round17 聚焦复审（改动=比较点视图+文案分流；重点：wide_landing 分流谓词误分面、
  T6/T8 补点对 rsync/分列 -t 语义分叉、绝对形双代差分零漂移复证）。


---
## Round18（2026-09-23）— F-17-S1 紧邻前 token 门控收紧（round17 引入误拦回归复位）
- 终审抓到 round17 1f 补点 search 非紧邻=源位读红线破口（第八次名实：注释「前随」
  ↔实现 search）。PM 双代差分独立坐实后立项 0098ebd。
- 子代理 sa-0-864a271a 交付撞 provider 错误（第 11 次），但 §A 制品完整+代码三面
  落地（1a 分列支 TAIL 锚 + 1b 矩阵 -t 支别名形分闸 + 1c 末位启发 bind 否决，
  同谓词零新逻辑；规格「≤4 行」单点走不通 22/24 → 三点收紧到 24/24，偏差如实
  报告在 §A/CHANGELOG）。
- PM 独立复跑完成定义 5 项全绿：pm018 24/0、pm017 19/0 不回退、test 29+4+404、
  全链 verify 零失败、红线 9/9（含 -rt 方向对偶锁：绑 tilde 目标=拦、后随源位=放）。
- NOTES 随批：N-17-1 已改实；N-17-2 引号选项词族/-17-3 rule_key 别名键/-17-4
  无扩展名文案取舍 三项登记在册不修（接受边界内）。
- 在途：round18 聚焦复审（改动面 git diff 0098ebd..HEAD -- handler.py 三点收紧；
  重点：TAIL 锚与 cluster/-rt 交叠、1c bind 否决对「同 token 重复 -t 目标」代价形、
  绝对形双代全量零漂移亲跑、N-17-2 登记面行为零变化复证）。
