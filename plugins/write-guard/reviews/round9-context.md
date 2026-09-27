# round9 终审基线（2026-09-22 20:0x）

被审对象：workspace/write-guard（git round9 提交，handler.py 含 S-1~S-5 修复），
部署同代际。最高准绳不变：requirements/requirement-20260922-boundary.md。

## 本轮改动（fix-009，规格 reviews/fix-009-input.md，过程制品 reviews/fix-009.md）
- S-1 HIGH：`-o<file>`/`-O<file>` 粘连提取（_GLUED_O_RE，仿 -t 族）
- S-2 MED：_PS_WRITE_RE +Copy-Item|Tee-Object（别名 cp/tee 登记不修）
- S-3 MED：分段集追加单 `&`（引号感知不误切 URL；`>&` 残段实测仍 block）
- S-4 MED：_command_word 循环剔除 wrapper（sudo/time/env/nohup/runas+X=Y+前置选项词）；
  `sudo -u root cp…` 带值形**登记边界**（fix-009.md §4）
- S-5 MED：载体裸形剥壳 depth+1 递归（_BARE_CARRIER_RE，受 _NEST_DEPTH_LIMIT 门）
- N1 补锁向 TC-R9-26/27；TC-R9 共 27 条；_verify_r9.py 46 项

## 验收基线（PM 独立复跑背书，非转述）
test_handler ALL PASS 29+4+277；_verify_r9 46/0、r8 30/0、r7 30/0、r5 28/0、r3 25/0；
pm_verify_009 攻击形 1a-c/2a-b/3a-b/4a-c/5a-c 全 approve、NEG 行零回退。

## 收敛判据（不变）
- **立项仅限**：纳入范围（boundary §纳入 1-7）内的新旁路 / 纳入范围误拦 / 名实不符。
- 排除范围形态（引号劈 token、反斜杠奇偶族、变量间接/eval/编码混淆、
  sudo 带值形、PS 别名 cp/tee 等已登记项）→ 一律不立项，只许附录罗列。
- 已登记边界若要翻案须给出 boundary 条文依据。
- 双路均 PASS/PASS_WITH_NOTES（NOTES 不涉 handler 逻辑）→ 整体收敛。

## 红线复述
approvals.mode manual；rm -r 拦截；git push --force/sudo 永不白名单；
写保护四守卫保持激活；改名/复制不拦；cp 写配置弹审批；不碰框架 repo。
