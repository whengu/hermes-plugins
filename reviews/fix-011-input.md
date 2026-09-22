# fix-011 修复规格（round11：round10 双路回归修复，最小批）

基线：git 9c33dcc（round10 已部署），292 new 用例 ALL PASS。
最高准绳不变：requirements/requirement-20260922-boundary.md。
本批 2 条实质 finding 是**双路同根互证**的 round10 修复引入回归（PM 全形实测背书：
reviews/fix011-scratch/pm_verify_011.py，OLD=r9 对照 block→PASS / PASS→block 实锤）：
- i/k/l/j=PASS（旧 block）、m=approve（旧 block）、o/p/q/r=block（旧 PASS）；
- 锁形 n/t/u/v/w 零回退。
双路报告：reviews/audit-round10-sec/review-010-sec.md §二（F-10-1/F-10-2）+
reviews/audit-round10-qual/review-010-qual.md（Q10-1/Q10-3 + NOTES Q10-2/Q10-4）。

## F-10-1（MED，双路=Q10-1）复制族「命名目标前置位」双向缺陷
- 漏拦向：`Copy-Item -Destination <CFG> <非保护>`、`Tee-Object -FilePath <CFG> -InputObject x`
  及 pwsh 载体/sudo 组合同形 → PASS（复制族判定只认末位路径与 cp/install 的 -t 支，
  前置命名目标无支可落）。
- 误弹向：`Copy-Item -Destination <非保护> <CFG>`（CFG 实为源）→ approve（末位启发
  把源当目标）。
- **修法（定死，≤5 行，比照 -t 支同款结构）**：在 `_terminal_position_is_write` 的
  `if cmd in _COPY_CMDS:` 块内、末位分支**之前**加命名目标支：
  新正则（模块级，仿 _COPY_T_RE 命名 `_PS_NAMED_TARGET_RE`）：
  `re.compile(r"-(?:Destination|FilePath|Path|Container|LiteralPath)\s*$", re.IGNORECASE)`
  分支逻辑：`cmd in ("copy-item", "tee-object") and norm 命中受保护
  （home 内路径 or 守卫文件，复用现有判定谓词） and _PS_NAMED_TARGET_RE.search(before)`
  → return True（本 token 即写目标）。
  - 该支同时修两向：前置 CFG 命中 → True（封堵）；反向形 `Destination <非保护> <CFG>`
    中 CFG 的 before 不含 Destination 紧邻（before 是 `…<非保护>`）→ 命名支 False →
    继续走末位分支——**注意末位分支仍会把 CFG 判目标（误弹向根源在末位启发）**，
    故命名支命中过（本段存在 `-Destination` 或 `-Path` 等显式绑定）时须**否决末位启发**：
    实现上取"段内含 PS 命名目标标志（search 全段）→ 末位分支仅当末位 token 即该
    标志的绑定值时才判写"。以 pm_verify_011 的 m 行（期望 PASS）与 i/j/k/l（期望
    approve/block 按写配置=approve 处置分流）实测为唯一裁决标准。
- **PS 语义正确性红线**：`-Destination <非保护>` 时 CFG 是源 → 必须 PASS（复制不拦）；
  不得为省事把"段内出现 -Destination"直接全判写（那会把反向形重新误弹——round9
  F-9-1 修复初衷回潮）。
- 引号/大小写/反斜杠/cd 链式负例随 TC；Set-Content 族「出现即写」支不回潮。

## F-10-2（LOW，双路=Q10-3）`[-/]o` 短形放宽误命中路径 token
- 复测形：`sort D:/myagent/workspace/o <CFG>`、`…/O <CFG>`、`curl http://x/o <CFG>`、
  `wget http://x/f/o <CFG>` → block（旧 PASS）；无写语义纯读被误拦。
- **修法（定死，≤3 行，与 F-9-3 同点收敛）**：`_OUTPUT_FLAG_RE` 短形组加 token 独立
  约束——`(?:--output-document|--output)\s*(?:=\s*)?$` 保持，短形拆成
  `(?:^|(?<=\s))[-/]o(?:\s|$)` / `(?:^|(?<=\s))[-/]O(?:\s|$)` 语义：即
  `r"(?:(?:--output-document|--output)\s*(?:=\s*)?|(?:^|(?<=\s))[-/]o(?:\s|$))"`
  注意锚 `$` 语义调整：before=「本 token 前文」，判据是**前一 token 独立等于 /o 或 -o**，
  故正确形态为 `(?:^|(?<=\s))[-/]o\s*$`（短形允许尾随空格消费）。探针 r10s_probe_h
  预演结论为准：curl/wget/sort 的 `-o `/`-O `/`/O `/cluster `-sSL -o ` 保持命中；
  `http://x/o `、`workspace/o `、`my-dir-o ` 不命中。
- 顺带归正附录⑥旧 FP（`sort …/my-dir-o <CFG>` 两代同陷 dash 同根）——若该形由同约束
  自然归正则一并锁 TC；若仍 block 则登记不动（以实测定，不得虚声称）。
- _GLUED_O_RE 粘连链（`-oD:/…`、`/OD:/…`）零回退（t/u/v/w 锁形实测背书）。

## 随批 NOTES（文档级，Q10-2/Q10-4）
- fix-010.md §1 补 [DONE F-9-1] 记录（子代理留"待补"）。
- `_prev_command_word` 死函数删除（L606，0 调用点，PM 实测）。
- CHANGELOG round10 节"末位/命名目标判定"失实句修正（Q9-N2 同型错误**第三次**，
  round11 节必须写明"命名目标支为 round11 补建"）。

## 过程与制品纪律（硬红线）
1. 先建 reviews/fix-011.md 骨架（§0 行为映射/§1 命名目标支/§2 o 约束/§3 NOTES/§4 验收），
   每步立即落盘带 [DONE] 标记。历史上 6 次截断丢产物——本条违反=返工。
2. 改动先 compile 再落盘；锚点先 grep 现场。
3. TC-R11 ≥12 条：F-10-1 四向（前置漏拦封堵/反向误弹归正/尾位锁形零回退/Set-Content
   不回潮）+ F-10-2 四形归正 + cluster 粘连锁形 + 附录⑥形（按实测方向锁）。
4. _verify_r11.py 建好（pm_verify_011 十六行翻转断言全覆盖 + 回归负例）。
5. CHANGELOG round11 节 + Q10 失实句修正。
6. 验收：`python test_handler.py`、`_verify_r11/r10/r9/r8/r7/r5/r3`、
   `python reviews/fix011-scratch/pm_verify_011.py`（i/j=approve 或 block 按写配置
   分流、k/l=命中、m=PASS、o/p/q/r=PASS、s=按实测、t=PASS、u/v/w=不弱于现状）。
   **红线复核用 on_pre_tool_call 入口**：gateway restart block、cp 写配置弹卡、
   Copy-Item 源位读 PASS（F-9-1 修复不回潮是本批最大回归风险）。
7. 不要 git commit、不要 deploy。终答 ≤250 字。
