# fix-015 修复规格（round15：S14-1 cluster 零 dash 误拦收窄 + NOTES 三处）

基线：git 27e0921（代码面 = 8611f3c 态，handler sha 前16=0a93ac9caf8ee25e，363 用例
ALL PASS）。准绳：requirements/requirement-20260922-boundary.md（本批=误拦向，红线邻近
"零误拦优先"，必须修）。

## 立项依据（双路同根互证 + PM 第三路复验+修法定演）
- sec S14-1（MED）：`_OUTPUT_QUOTED_RE` cluster 支 `[-]?` dash 可省 → `curl "Cairo" <CFG>`
  / `sort "logo" <CFG>` 引号字母 o 尾词+受保护段实锤 block（PM 复验坐实；裸形同义=PASS，
  唯一切换量=引号）。
- qual Q1（NOTES 同根）：零 dash 放行 `"o"/"O"` 与注释「单 dash 专属」名实不符。
- qual Q2（LOW·NOTES）：CHANGELOG round14/fix-014.md §A-A4 死选项机理句失实——curl
  `--output=` 端实测 rc=2 option unknown（非「=并入文件名」，后者系 `-sfo=` cluster 短形
  机理，8dde55e 档案）。**PM 认定属实**（round14 节是我方撰写，第五次教训口径）。

## 修法定演（PM 内存猴补丁实测，11 形全符合）
改动1（1 字符）：第三交替支 `|[-]?[a-zA-Z]*[oO]` → **`|- [a-zA-Z]*[oO]` 去问号后的
`|-[a-zA-Z]*[oO]`（dash 必选，无空格；替换式即 `old.replace("|[-]?[a-zA-Z]*[oO]",
"|-[a-zA-Z]*[oO]")`，PM 已实测 pattern 锚唯一匹配）**。实测矩阵：
- FP 消除：`curl "Cairo" CFG`=PASS、`sort "logo" CFG d`=PASS
- 靶心保持：T11 `-so`/T12 `-sSo`/T13 `-qO`/T14 `-ro` 全 block；`"-o"`/`"-O"` r12 锁 block；
  E1 `"-o<CFG>"` block；T18 `"-oL"` PASS
- 新现值：`curl "o" CFG`（零 dash）→ PASS（与注释名实归正，登记 TC 锁向）

## 改动2（NOTES，全部实测背书）
1. CHANGELOG round14 节 A4 句 + fix-014.md §A 机理改实：curl `--output=` 系端 rc=2
   不可运行形（「=并入文件名」机理归 `-sfo=` 短形专属，引 8dde55e 档案）；定级/多防结论不变。
2. CHANGELOG round15 新节：S14-1 修复 + 教训句「正则放宽类改动，字符类每个可选项必须
   与注释承诺逐词对拍（『单 dash 专属』承诺 vs `[-]?`）」。
3. qual Q4：pm_verify_014 头部注释旧口径「29 形/16 靶心」改实为「27 形/13 靶心」。
4. qual Q5 排版随批（如点名行）。

## 改动3（测试锁）
- TC-R15 ≥4 条：`curl "Cairo" <CFG>`=PASS、`sort "logo" <CFG> d`=PASS（FP 锁）、
  `curl "-so" <CFG>`=block、`curl "o" <CFG>`=PASS（新边界锁）。
- pm_verify_014 追加 T19/T20 两 FP 形（want=pass）——**改后 29/0**（此 2 形当前 FAIL=本批靶心）。
- _verify_r14 保持 43/0 不回潮。

## 完成定义（PM 门禁复跑清单）
1. `python reviews/fix014-scratch/pm_verify_014.py` → **29 形 0 失败**（含新 T19/T20）
2. `python test_handler.py` → ALL PASS（363+4 量级）
3. `python _verify_r14.py` → 43/0；`python reviews/fix013-scratch/pm_verify_013.py` → 30/0
4. 九 verify（r13~r3）全零失败；`python reviews/fix012-scratch/pm_verify_012.py` 零 FAIL
5. 红线四形（on_pre_tool_call）：gateway=block、cp 配置=approve、Copy-Item 源位读=PASS、
   `-Destination CFG WS`=approve
6. CHANGELOG 新句逐词实测背书（每个数字/机理句先跑再写）

## 纪律
不改 deploy/plugin.yaml；不 git commit、不 deploy；制品 reviews/fix-015.md 第一步建骨架
每步 [DONE]；探针 ≤10 分钟；终答 ≤150 字只给门禁数组+文件清单。
