# fix-012 修复规格（round12：命名支收窄 + 冒号粘连 + 引号选项词 + cluster 尾o）

基线：git 94998f5（round11 已部署），309 new 用例 ALL PASS。
准绳：requirements/requirement-20260922-boundary.md。
行为基线：reviews/fix012-scratch/pm_verify_012.py（PM 实测 23 行，直接引用为步骤 0）。
双路报告：audit-round11-sec/review-011-sec.md（F-11-1~4）+ audit-round11-qual/review-011-qual.md（Q-11-1）。
F-11-3 与 Q-11-1 同根，一条修。根因链透明记录：F-11-3 的绑定词表出自 PM 所写
fix-011-input 清单（把 -Path/-LiteralPath/-Container 与目标词并列）——规格里已注明。

## 改动 1（F-11-3+Q-11-1，MED 向红线）_PS_NAMED_TARGET_RE 收窄目标词
- 现状（实测 c1/c2/c5=approve）：五词表把源参当目标绑定词。
- 修法（1 行）：TARGET 词表 → `-(?:Destination|FilePath)\s*$`（IGNORECASE 保持）。
  **_PS_NAMED_ANY_RE 五词表不动**（末位否决仍需 Path/LiteralPath 在场信号）。
- 期望（PM 已推演全支路）：c1/c2/c5 → PASS；c4 `-Destination <CFG> <非保护>` 与
  c6 `Tee-Object -FilePath <CFG> x` 封堵保持 approve/block 向；c3 反向锁形保持 PASS；
  双标志 B 锁形（-Container CFG -Destination 非保护）保持 PASS。

## 改动 2（F-11-1，LOW 旁路）PS 命名目标冒号粘连形
- 现状（实测 a1/a2/a3=PASS，pwsh 活证可运行真写）。
- 修法（≤4 行，比照 _GLUED_T_RE 先例）：新正则
  `_GLUED_NAMED_RE = re.compile(r"^-(?:Destination|FilePath):(['\"]?)(\S+?)\1$", re.IGNORECASE)`
  （引号值 a3 一并吃下；等号形/全词粘连 pwsh 拒绝=附录不修）。在 -t/-o 粘连提取的
  同一收集位点提取值段进 norm，判定走改动 1 后的命名支语义（本 token 即绑定值→写）。
- 期望：a1/a2/a3 转命中（写配置=approve 处置分流）；a4 保持 PASS（登记附录）；
  非保护值 `-Destination:D:/ws/x` 不命中。

## 改动 3（F-11-2，LOW 旁路）引号包输出选项词 `curl "-o" <CFG>`
- 现状（实测 b1/b2/b3=PASS，curl 活证剥引号同义真写；纳入3 明文义务面）。
- 修法（≤3 行）。**PM 修正 sa-0 提案缺陷**：其正则 `(?:...)?` 把选项内容设为可选，
  会命中任意引号 token（""/''/任意字符串）——内容部分不得可选：
  `_OUTPUT_QUOTED_RE = re.compile(r"[\x27\x22](?:-[oO]|--output(?:-document)?)[\x27\x22]\s*$")`
  并入 `_OUTPUT_FLAG_RE.search(before) or _OUTPUT_FLAG_EQ_RE…` 同款判定式。
  不做通用引号剥离（F-7-2 禁令不回潮）。
- 期望：b1/b2/b3 转命中；b4 grep "-o"（门外）保持 PASS；b5 `curl "-O" <url>`
  红线向保持 PASS；`curl "-o" <非保护>` 不命中。

## 改动 4（F-11-4，MED 旁路）o 收尾 cluster + 空格值 `curl -so <CFG>`
- 现状（实测 d1~d4=PASS，curl 活证 getopt cluster 尾 o 带独立值同义真写）。
- 修法（≤3 行，_OUTPUT_FLAG_RE 短形组并支，dash 专属）：
  追加 `(?:^|(?<=\s))-{1,2}[a-zA-Z]*o` 支（**斜杠方言不参与**——cmd 无 cluster
  语义，F-10-2 归正不回潮）。
- 期望：d1~d4 转命中；d5~d8 负例保持 PASS；d9/d10（sort ws/o、http://x/o 族）
  保持 PASS 不回潮；`curl --http1.0 <CFG>` 类数字尾不命中（[a-zA-Z]* 不吃 0）。

## NOTES 随批（质量路微疵）
- fix-011.md §0 补 [DONE] 标记；TC-R11-12↔15 编号笔误两处修正。
- CHANGELOG round12 节：根因链如实记载（改动 1 词表出自 round11 规格清单的并列错误）。

## 过程与制品纪律（硬红线）
1. 先建 reviews/fix-012.md 骨架（§0 行为映射/§1~4 各改动/§5 NOTES/§6 验收），
   每步立即落盘带 [DONE] 标记。历史上 6 次截断丢产物。
2. ≤10 分钟探针后必须开始改代码——规格已定死到正则，照图施工禁止再设计。
3. TC-R12 ≥16 条：四改动各 ≥2 封堵 + 全部上表负例锁 + c3/c4/c6/B 四条 r11 锁形零回退。
4. _verify_r12.py：pm_verify_012 23 行翻转断言 + 回归负例全集（含 _verify_r11 的
   F-9-1 源位读红线形、pm_verify_011 的 o 族归正形）。
5. 验收：`python test_handler.py`、`_verify_r12/r11/r10/r9/r8/r7/r5/r3`、
   `python reviews/fix012-scratch/pm_verify_012.py`（按上表期望）、
   `python reviews/fix011-scratch/pm_verify_011.py`（16 行零回退）、
   红线三形 on_pre_tool_call（gateway block/cp 弹卡/Copy-Item 源位 PASS）。
6. 不要 git commit、不要 deploy。终答 ≤250 字。
