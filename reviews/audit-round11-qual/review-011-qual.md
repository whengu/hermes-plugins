# review-011-qual — write-guard round11 终审（质量路，只读）

- 日期：2026-09-22　基线：git 94998f5（round11 FIX 闭环，工作区 = HEAD，未 commit/deploy 纪律由 PM 侧闭环）
- 探针：本目录 r11q_{collateral,diff,diff9,susp,sha}.py（全部 on_pre_tool_call 正确入口；现场活证：探针构造期写 /tmp 被守卫 C 实拦改道）

## 裁决：**CHANGES REQUIRED**（1 条实质 finding Q-11-1 MED，系 round11 新引入纳入范围误拦；NOTES 2 条文档级）

## 一、实跑验收（全绿，独立实跑非转述）

| # | 项 | 结果 |
|---|---|---|
| 1 | python test_handler.py | **ALL PASS (29 scan + 4 hook + 309 new)** ✅ 与预期 29+4+309 逐字一致 |
| 2 | _verify_r11 / r10 / r9 | 43/0、46/0、46/0 ✅ |
| 3 | _verify_r8 / r7 / r5 / r3 | 30/0、30/0、28/0、25/0 ✅ 无回潮 |
| 4 | pm_verify_011 十六形 | i/j/k/l=approve、m=PASS、n=approve、o/p/q/r=PASS、s=PASS、t=PASS、u/v/w=block——与 §0 表全达 ✅ |
| 5 | matrix_r11 十六形外延 | LiteralPath/Container/Path 前置仅=approve（→ 见 Q-11-1 定性）、引号标志=PASS、dest 带引号值=approve ✅（现状锁与 fix-011 §4 登记一致） |
| 6 | 红线三形 | gateway restart=block、cp 写配置=approve 弹卡、Copy-Item 源位读=PASS（F-9-1 不回潮，末组实测）✅ |

## 二、名实一致性逐句对拍

1. **_PS_NAMED_TARGET_RE 尾锚注释**（L264-266）：`-(?:Destination|...)\s*$` 对 `before=seg[:start].rstrip()`——"本 token 紧随标志即其绑定值"名副其实 ✅；ANY_RE "段内出现过该族标志（末位启发否决依据）"与 L700/706 `named` 用法一致 ✅；`-Destination 非保护 CFG` 源位不再误弹=m 形实测 PASS ✅。
2. **双标志语义**（L695-699 注释 vs L700-703 代码）：前置命中+`seg[m.end():]` 无后继标志才判写——`-Container <CFG> -Destination 非保护` r10 锁形 B 仍 PASS（TC-R11-06/06 复测+差分佐证）✅ 三条守卫逐句对应，无虚词。
3. **F-10-2 "长形与 = 粘连链语义不变"**：diff 2cc28cf..HEAD 证实仅短形组 `[-/]o|[-/]O`→`(?:^|(?<=\s))[-/]o`（IGNORECASE 承担 /O），两长形 alternate 与尾锚 `\s*(?:=\s*)?$` 逐字未动；= 粘连链 _OUTPUT_FLAG_EQ_RE/_GLUED_O_RE 独立正则零改动，r11q_diff 实测 `-sSL -oCFG`/`sort /O`/`-o ` 锁形全同向 ✅。注释"前随空白/段首"与 lookbehind 语义相符（`/O` 前随空格实测仍 block，v 形）✅。
4. **CHANGELOG round11 节**：16 形预期值逐条与实跑一致；"Set-Content 族出现即写不回潮"（block 实测）、"无命名标志的 cp/copy/install/rsync 路径零行为差"（§三差分实测 0 差）均属实，无新失实句 ✅。
5. **fix-011.md 五节 [DONE]**：§1/§2/§3/§4 有 [DONE]，**§0 无 [DONE §0] 收尾标**（input §59 纪律"每步立即落盘带 [DONE]"，round10 先例 fix-010.md 有 [DONE §0]）——微疵，并入 NOTES。**§2 末行"TC-R11-12"应为 TC-R11-15**（§0 表行 s 的依据列同误；实测锁定在 TC-R11-15，L1088）——笔误 NOTES。
6. **round10 失实句修正**：CHANGELOG L45 原句已改「末位目标判定」+ L47-50 Q10-1 修正句显名"无中生有失实——round10 落地时命名目标支并不存在…系 Q9-N2 同型失实第三次"；handler L257-258 补 round11 补建归因；fix-010.md §1 标题行 [DONE F-9-1] + 后记（round11）段补记完整。三处口径互证一致，**修正到位** ✅（第三次失实已显名登记）。
7. **附录⑥"自然归正"声称**：溯源 review-010-sec §四.6 真实存在（dash 同根旧 FP，两代 block，探针 f 实测 old 同陷）；`sort …/my-dir-o <CFG>` r11q_diff 实测 r10=block→r11=PASS——同约束切断 `-o` dash 尾锚，"自然归正"非虚称，TC-R11-15 按实测方向锁定 ✅。附录编号 ③④⑥ 与源报告节次对应无误。

## 三、末位启发否决连带面独立回归（27 例现行为 + r10 代际差分 + r9 代际差分）

- **现行为断言 27 例**（r11q_collateral）：cp 末位目标弹卡/源位读、`cp -t HOME`/`-rt` 簇/粘连 `-t<dir>`/install -t、**rsync -t 纯读（R4-1）PASS 且 rsync 末位目标仍 approve**、robocopy 三参 PASS、cmd `copy /Y` 弹卡/copy 源位读、`copy -t`（cmd 方言非 PS 零差）、sort `/O` `/o` block、curl `-o` block、curl/wget URL `/o` 归正、Tee-Object -FilePath approve、Set-Content/Out-File block、grep `-o` 未知命令放行、-LiteralPath 双标志 PASS、pwsh 载体正反两向——25 例与预期符；2 例（sed -i=block、mv=PASS）系本矩阵无写目标语义/处置分流口径，经代际差分证明非本轮变化。
- **r10 基线差分**（r11q_diff，27 列）：**仅 5 例变化，逐一 = §0 预期翻转**（m 反向归正、o/p 两形、s 附录⑥、i/k 载体正反向对）；cp/-t 支、copy 混用 /Y、rsync、robocopy、sed、tee、Set-Content 面全部 SAME——**否决连带面零意外变化** ✅。
- **r9 代际差分**（r11q_diff9，13 列）：2 例变化均为 Copy-Item 源位读（r9 block→r11 PASS），系 F-9-1 摘出既定向（round10 §0 联动翻转同款登记），非 round11 引入。

## 四、实质 finding

### Q-11-1（MED·round11 新引入纳入范围误拦）TARGET 五标志把 -Path/-LiteralPath/-Container 当写目标——Copy-Item 源位标志被前置判写

- **复现**（r11q_susp 实测）：`Copy-Item -Path <CFG> <非保护末位>` r10=**PASS → r11=approve**；`Copy-Item -LiteralPath <CFG> D:/x/b.txt` 同陷；`Copy-Item -Container <CFG> <非保护>` 同陷（-Container 非 Copy-Item 实参，冷形）。该形为合法常用 PS：-Path 绑源、位置参绑 -Destination=目标，**CFG 实为读源**——违背"源位=读不拦"红线（F-9-1 修复初衷的 -Path 前置同族回潮，round9 S-2→F-9-1 即为此例先修后分叉）。
- **旁证（判定冗余）**：`Copy-Item -Path <CFG> -Destination <非保护>` = PASS——ANY_RE 末位否决已正确兜住同语义形；TARGET 支对 -Path/-LiteralPath 不仅误判且**无必要**。反例形 `-Destination <CFG>` 的封堵仅依赖 Destination/FilePath 两词即成立（i/j 实测）；-Container 在封堵向唯一用例是双标志锁形 B，而该形恰靠 ANY_RE 否决通过。
- **根因归位**：fix-011-input §21 定死五词清单"照图逐字符落地"——子代理无越权，失实在立项规格（PM 责任面）。第 4 次"名实"型缺陷，然此次为行为向，非文档句。
- **修法方向（≤1 行，不扩面）**：`_PS_NAMED_TARGET_RE` 词表收缩为 `(?:Destination|FilePath)`（前置封堵两词已足，i/j/k/l 十形不受损）；`_PS_NAMED_ANY_RE` 五词保留（否决面越宽越保守，PASS 向无害）。回潮锁：TC-R11-06 双标志、m 形、i/j/k/l、matrix Path 前置仅=approve→改后应 PASS，按实测方向改锁。

## 五、NOTES（文档级，随批）

1. fix-011.md：§0 缺 [DONE §0] 收尾标；§2/§0 表"TC-R11-12"应为 TC-R11-15 两处笔误。
2. pipeline-status.md 未落 round11 行（表末仍 round10/2cc28cf/292；门禁基线段仍书 HEAD 90de321/233 stale）——按轮次惯例系终审收敛后 PM 更新，登记提醒勿忘；部署实测三镜像 handler=65f7c1b4ff58f6ef 与源全同（r11q_sha BAD=[]，__init__/plugin.yaml 同代际）。

## 六、AST/长行/死代码

AST parse OK（29 顶层 def，py_compile 双文件过）；handler.py >120 行 **0 条**（N3 口径）；死代码：`_prev_command_word` 活库 5 文件 grep=0（残留仅在 reviews/ 代际快照与 round10 探针存档，不属活码）；`on_pre_tool_call` 仅 1 定义命中系 __init__.py hook 注册引用，非死。零新死码。

## 七、结论

验收链 1-6 全绿、名实对拍 6/7 项到位、连带面差分干净——但 Q-11-1 为 round11 新引入的 PS 源位误拦（红线向，纳入范围 6），按"双路同根互证"口径立项下一批（round12）修正。裁决 **CHANGES REQUIRED**。
