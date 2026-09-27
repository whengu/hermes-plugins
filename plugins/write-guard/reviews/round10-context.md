# round10 终审基线（2026-09-22 21:5x）

被审对象：workspace/write-guard（git round10 提交，round10 已 deploy，主部署+双镜像同代际）
+ design/requirements 文档口径 + 部署一致性。最高准绳不变：requirements/requirement-20260922-boundary.md。

## 本轮改动（fix-010，规格 reviews/fix-010-input.md，过程制品 reviews/fix-010.md）
- F-9-1 Copy-Item/Tee-Object 摘出 _PS_WRITE_RE 并入 _COPY_CMDS 复制族判定（源位不拦红线）
- F-9-2 新增 _strip_wrapper_prefix，载体识别入口改用剥离后文本（wrapper×载体通道，单点）
- F-9-3 _GLUED_O_RE/_OUTPUT_FLAG_RE 短形组字符类 ^- → ^[-/]（cmd 原生 sort /O 方言）
- F-9-4 tee 判据由 prev=='tee' 改 _command_word(seg)=='tee'（非末位多目标）
- Q9-N1/N2/N3 登记项；TC-R10 15 条；_verify_r10 46 项

## 验收基线（PM 独立八项复跑背书）
test_handler ALL PASS 29+4+292；_verify_r10 46/0、r9 46/0、r8 30/0、r7 30/0、r5 28/0、r3 25/0；
红线经 on_pre_tool_call 正确入口复测：gateway restart block（含 bs+LF 续行形）、status 不误伤、
cp 写配置弹卡 approve、rm -r 平台分层不变。

## 收敛判据（与前轮一致）
- 立项仅限：纳入范围（boundary §纳入 1-7）内新旁路 / 纳入范围误拦 / 名实不符。
- 排除范围形态与全部已登记边界 → 一律不立项，只许附录罗列。
- 双路均 PASS/PASS_WITH_NOTES（NOTES 不涉 handler 逻辑）→ 整体收敛，进入 gateway 重启+终版报告收尾。

## 本轮 PM 特别提请复审关注的两处
1. **入口口径**：`_judge_terminal` 仅覆盖 A/B 守卫路径；gateway（守卫 D）与四守卫完整链在
   `on_pre_tool_call`。复审探针请用正确入口，勿把入口用错的 PASS 报成旁路（本轮已有一例：
   误用 _judge_terminal 测 gateway restart 得 PASS，改 on_pre_tool_call 即 block，系探针入口错非缺陷）。
2. **F-9-1 四向③处置**：`Copy-Item <非保护源> <守卫源码/目录>` 实测 approve——这是复制族既有
   口径（TC-A-46 同款），非"写守卫文件→block"。若复审认为该处置不当，需同时论证 cp 同款是否
   一并改（属跨轮决策非本轮 bug），单报 Copy-Item 分叉不成立。
