# fix-013 修复规格（round13：PS per-cmd 目标表 + 引号粘连选项值）

基线：git 8dde55b（round12 部署 4e254c8 后仅文档提交），329 new 用例 ALL PASS。
准绳不变：requirements/requirement-20260922-boundary.md。
来源：安全路 F-12-1/F-12-2（=PM X-13 候选独立复核成立）+ F-12-3（引号粘连选项值）。
全部 pwsh/curl 活证真可执行（非理论形），详见
reviews/audit-round12-sec/review-012-sec.md 与 reviews/fix013-scratch/pm_probe_013_pre.md。

## 验收唯一标准（先跑这个，它就是完成定义）
`python reviews/fix013-scratch/pm_verify_013.py`
当前实测：通过 19 失败 11——11 条 FAIL 全部转绿且 19 条 ok 不回退 = 本批完成。
另加 test_handler + 七 verify 全绿、红线三形（on_pre_tool_call）。

## 改动 A（F-12-1+F-12-2 合并，per-cmd 目标表）handler.py L265-280 + L718-726
根因：round12 把"目标标志"做成 cmd 无关全局集，且前置支否决子句把"后随任意命名
标志"都当目标移交。PS 真语义（pwsh 活证）：
- Copy-Item：目标={-Destination}；-Path/-LiteralPath/-Container=源参
- Tee-Object：目标={-FilePath, -LiteralPath}（-LiteralPath 在 Tee 是输出目标！）
修法（≤10 行，零新解析层）：
1. per-cmd 目标词表（dict 或按 cmd 分支皆可）：
   `_PS_TARGET_FLAGS = {"copy-item": r"Destination", "tee-object": r"FilePath|LiteralPath"}`
2. 前置支（L718-722）条件重构：
   - "本 token 是命名绑定值" = before 尾锚 `-<本cmd目标词>\s*$`（参数化替换
     _PS_NAMED_TARGET_RE 的固定词表）或 raw 命中冒号粘连且标志∈本 cmd 目标词
     （_GLUED_NAMED_RE 同步参数化或新建按 cmd 版）；
   - 否决子句 `not _PS_NAMED_ANY_RE.search(seg[m.end():])` 改为
     **`not <后随段中"本 cmd 的目标族标志"再次绑定值>`**（逐 cmd，禁全局并集——
     否则 X2 `Copy-Item -Destination CFG -LiteralPath ws` 会被 Tee 的目标词
     LiteralPath 误否决）。等价简化规则（PM 推演全锁形通过，推荐照此实现）：
     「本 token 判写 = before 尾锚**本 cmd 目标标志** 或 raw=冒号绑定本 token 为目标值；
     本 token 判读(PASS 且否决末位启发) = 段内本 cmd 目标标志已绑定**另一个**值；
     段内本 cmd 无目标标志绑定 = 走末位启发（POSIX 位置参形）。」
     据此复推：X1/X2/X3/X4/T1~T3→命中；K2/K4/K11→PASS（Destination 已绑非当前 token）；
     K3/K5→PASS（CFG 绑源标志且无目标标志绑定、CFG 非末位）；K6/K7→命中；
     Tee -FilePath <ws> -LiteralPath <CFG> 双目标绑定=PS 报错误形，fail-closed
     允许弹卡，TC 锁实测值。
3. 末位否决子句（L725-726）`(not named or _PS_NAMED_TARGET_RE.search(before))`
   同步用 per-cmd 目标尾锚语义。
4. `_PS_NAMED_ANY_RE` 保留原五词作"命名标志在场"检测（named 前置条件不变）。
锁形依据（改后必测）：K2/K3/K4/K5/K11 保持 PASS；X1~X4/T1~T3 转 approve|block。

## 改动 B（F-12-3，引号包「选项+粘连值」）handler.py _GLUED_O_RE 邻域
现状：`curl "-so<CFG>"`/`"-o<CFG>"`/`'-O<CFG>'` PASS——引号吞掉整串 token，
`[^\s;&|<>()]+` 收整个含引号 token，_GLUED_O_RE `^[-/]…` 被首字符引号挡住。
修法（≤3 行，比照 _GLUED_T_RE 引号处理先例——先看 L283 _GLUED_O_RE 与收集处
norm_raw 逻辑，最小方案=匹配前对 raw 剥**成对**外层引号一处 `raw.strip("'\"")`
或正则前置 `['\"]?`；禁止通用引号剥离进 token 化（F-7-2 禁令））。
锁形依据：K13 grep "-o" 门外保持 PASS；K14 curl -O URL 红线保持 PASS；
E1~E4 转 block；K17/K19 无回退。

## NOTES 随批
- CHANGELOG round13 节：根因链如实记载（round12 TARGET 收窄引入 F-12-1 回退
  r11 已有能力——这是修复引入回归第 3 次，写进"过程教训"）；curl `=` 形附录句
  （等号并入文件名的活证结论）补登。
- fix-012.md 若留有未闭环句顺手补。

## 过程与制品纪律（硬红线）
1. 先建 reviews/fix-013.md 骨架（§0 行为映射/§A/§B 落地记录/§N NOTES/§V 验收），
   每步立即落盘 [DONE]。
2. ≤10 分钟探针后动代码（锚点本规格已给：L265-280/L718-726/L283/L949）。
3. TC-R13 ≥13 条：X1~4/T1~3/E1~4 封堵 + K2/K4/K13/K14 代表锁形（新支交叉面）。
4. _verify_r13.py 生成（或直接扩断言跑 pm_verify_013 亦可，但 TC 必须进 test_handler）。
5. 验收全实跑：test_handler（预期 29+4+≥342）、_verify_r13、
   `python reviews/fix013-scratch/pm_verify_013.py`（0 失败）、_verify_r12/r11/r10/
   r9/r8/r7/r5/r3 全零失败、红线三形 on_pre_tool_call、
   pm_verify_012 无回退（23 形期望与现状一致）。
6. 不要 git commit、不要 deploy。终答 ≤200 字。
7. 发现规格修法走不通时：**停下如实报告**，不要自行换设计（前例：round8 规格
   笔误由实现者实测纠正获认可的是行为等价修正，架构级偏离必须报告）。


## PM 活证补充（01:4x，实现前必读）：双目标标志绑定 = PS 必然报错
pwsh 活证：`Copy-Item -Destination A -Destination B` 报
"Cannot bind parameter because parameter 'Destination' is specified more than once"
且**整条不执行零写**（_zb.txt 未生成）。∴
- Z1 `-Destination <CFG> -Destination <ws>` 现值 PASS = 语义正确（无写副作用），
  **TC 锁 PASS，不得"顺手封堵"**；
- Z2 `-Destination <ws> -Destination <CFG>` 现值 approve = 保守方向（对必败形弹卡
  无害），TC 锁实测值即可，不要求改；
- Z3 `Tee -FilePath <ws> -LiteralPath <CFG>` 现值 PASS，同 Z1 锁 PASS。
三分句规则（"段内本 cmd 目标标志已绑定另一个值→判读"）天然导出 Z1/Z3=PASS，
与活证一致——实现者只需验证，勿为 Z 组加特判。
