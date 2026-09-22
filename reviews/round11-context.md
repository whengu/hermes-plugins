# round11 终审基线（2026-09-22 23:2x）

被审对象：workspace/write-guard（git round11 提交）+ 部署同代际。
最高准绳不变：requirements/requirement-20260922-boundary.md。

## 本轮改动（fix-011，规格 reviews/fix-011-input.md，过程制品 reviews/fix-011.md）
- F-10-1（MED，round10 引入回归）：Copy-Item/Tee-Object 命名目标**前置位**双向缺陷——
  新增 _PS_NAMED_TARGET_RE（尾锚，本 token 紧随标志=写目标）+ _PS_NAMED_ANY_RE（段内
  出现过标志=末位启发否决依据）。前置漏拦封堵 + 反向源位误弹归正 + 双标志锁形保持。
- F-10-2（LOW，round10 引入回归）：`[-/]o` 放宽误命中路径 token——_OUTPUT_FLAG_RE
  短形组加 token 独立约束 `(?:^|(?<=\s))[-/]o`，附录⑥ `my-dir-o` 形自然归正。
- NOTES：死函数 _prev_command_word 删除；fix-010 §1 补记；CHANGELOG round10 失实句
  （"命名目标判定"无中生有，Q9-N2 同型第三次）修正。
- TC-R11 17 条；_verify_r11 43 项。

## 验收基线（PM 独立复跑背书，非转述）
test_handler ALL PASS 29+4+309；_verify_r11 43/0、r10/r9 46/0、r8/r7 30/0、r5 28/0、r3 25/0；
pm_verify_011 十六形全达标（i/j/k/l=approve命中、m=PASS、n=approve、o/p/q/r/s/t=PASS、
u/v/w=block）；红线三形（on_pre_tool_call）：gateway restart block、cp 写配置弹卡 approve、
Copy-Item 源位读 PASS；双标志 -Container CFG -Destination 非保护=PASS；6 负例零回退。

## 收敛判据（与前轮一致）
- 立项仅限：纳入范围（boundary §纳入 1-7）内新旁路 / 纳入范围误拦 / 名实不符。
- 排除范围形态与全部已登记边界 → 一律不立项，只许附录罗列。
- 双路均 PASS/PASS_WITH_NOTES（NOTES 不涉 handler 逻辑）→ 整体收敛。

## 特别提示（本轮已修面的回归验证点）
1. 探针入口用 on_pre_tool_call（四守卫全链）；_judge_terminal 仅 A/B 路径。
2. F-10-1 三锁形必复测：前置 -Destination <CFG>=命中、反向 <CFG 源位>=PASS、
   双标志 -Container <CFG> -Destination 非保护=PASS（目标另有其主）。
3. F-9-1 复制族源位读红线不回潮；cp 写配置弹卡不回潮。
4. 附录⑥ my-dir-o 归正已由 TC-R11-15 锁 PASS——若复审发现该约束令某真·输出标志形
   漏拦（如 `-o` 前无空格的粘连），那是 _GLUED_O_RE 链职责，先核 _GLUED_O_RE 是否命中再判。
