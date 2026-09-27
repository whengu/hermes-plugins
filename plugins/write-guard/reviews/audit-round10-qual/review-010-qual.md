# round10 终审·质量路（只读） review-010-qual

裁决：**CHANGES REQUIRED**（2 项纳入范围名实/漂移 + 2 项轻度制品/腐化项）

## 1. 实跑验收（全绿，与 §6 表八行逐一对读无失实）

| # | 命令 | 实测末行 | fix-010 §6 声称 | 一致 |
|---|------|---------|----------------|------|
| 1 | test_handler.py | ALL PASS (29+4+292) | 同 | ✅ |
| 2 | _verify_r10 | 46/0 | 46/0 | ✅ |
| 3 | _verify_r9 | 46/0 | 46/0 | ✅ |
| 4 | _verify_r8 | 30/0 | 30/0 | ✅ |
| 5 | _verify_r7/r5/r3 | 30/0、28/0、25/0 | 同 | ✅ |
| 6 | pm_verify_010b | A-D=PASS、E=PASS、F=approve、G-K=block、L-O=block、P/Q=approve | 翻转表逐行 | ✅ |
| 7 | 红线（on_pre_tool_call） | restart block（含 bs+LF 续行）、status PASS、rm -r 分层 PASS | 同 | ✅ |
| 8 | 四向锁 | 源位 PASS/目标配置 approve/守卫源码 approve/cp 对照零分叉 | 同 | ✅ |

无回潮确认：round9 联动翻转两条（S-2/S-5 Copy-Item 形）已在 _verify_r9 就地改向并注释归因（L48/85），非静默改预期。✅

## 2. 名实对读（四处改动 注释/CHANGELOG/fix-010 vs 实测）

- **_COPY_CMDS 并入**：L591-592 词表、L254-258 两组分支注释与实现一致；`_PS_WRITE_RE` 回退三词属实（git diff cbd6301..HEAD 核对）。但 **CHANGELOG L19「末位/命名目标判定」失实**→ 见 Q10-1。
- **_strip_wrapper_prefix**：载体入口单点改属实（diff 仅 L886-899 一处入口 +2 行 carrier_seg）；"无 wrapper 原样返回零行为差"实测成立（`cp a b` strip 后原样）。helper 体约 8 逻辑行，超 input"≤6 行"字面——N3 口径（核心逻辑）边缘，随 Q10-4 批注即可。
- **两处字符类 ^[-/]**：diff 确为 _GLUED_O_RE + _OUTPUT_FLAG_RE 各 1 处，与声称一致；但 _OUTPUT_FLAG_RE 是 curl/wget/sort 三门共用——斜杠形外溢 curl/wget → 见 Q10-3。
- **tee 判据 _command_word**：L683 一行改 + "全部位参皆目标"注释口径与实测一致（L/M/O/N 全对）。旧 `_prev_command_word` 全文件仅剩定义零调用 → 死函数腐化，Q10-4。
- **CHANGELOG Q9-N2 句（曾失实后修正）再验**：根因三句全部源码级复核成立——开关组 `[/-][A-Za-z]\w*` 第二字符 `--login` 非字母不消费；`\s+(?:-[lc]?c|…)` 遇 `--login` 断；strip 只剥前导词。**实测两形 PASS 与"登记不修"声称现名实相符** ✅。
- **Q9-N1 句**：`/usr/bin/ls <CFG>`、`/usr/bin/cp evil <CFG>` 两代（cbd6301 vs HEAD）同向 PASS 实跑背书 ✅（后者含 "/"开头词被当选项剔除的既有登记面，属 round9 S-4 已登记族，不重开）。
- **§0/§84-86 的 F-9-1 四向③偏离**（input 预期 block→实测 approve）：§0、CHANGELOG、round10-context 三处一致登记且论证成立（与 cp 同语义不分叉），判合规 ✅。
- fix-010.md **§1 仍为"（待补）"**（§2~§6 有 [DONE]）→ Q10-2。

## 3. F-9-1 连带面独立回归（22 例矩阵 + 7 例非末位命名形，脚本 probe_r10_qual_matrix.py）

末位/源位/目录/载体/对照 22 例：非保护目标 PASS、目录目标（带/无尾分隔符）approve、-Destination/-Container/-Recurse/-LiteralPath 末位形、cmd copy、pwsh 载体、Set-Content 不回潮、tee 负例——**零漂移** ✅。

**但发现两类基线回归（r9 cbd6301 vs r10 对跑）**：

### Q10-1（MED·漏拦回归+名实不符）命名目标非末位形
| 形 | r9 | r10 |
|---|---|---|
| `Copy-Item -Destination <CFG> evil.txt` | block | **PASS** |
| `Copy-Item -Destination <GD> evil.txt` | block | **PASS** |
| `Tee-Object -FilePath <CFG> -Append` | block | **PASS** |

复制族矩阵只有"末位路径=目标"启发（+cp/install 专属 -t 支），无任何 -Destination/-FilePath 命名支——"摘出现即写支"后 flag 前置形从巧合拦转裸漏。boundary §纳入7"复制/写入目标是守卫目录或 home 内配置文件"必修族内；且 CHANGELOG L19/注释"命名目标判定"系无中生有（Q9-N2 同款失实类，本轮复审特别要求再验的正是这类句）。**修法二选一（立项时定）**：比照 -t 支给 copy-item/tee-object 加 2 行命名目标提取；或改声称句 + 显式登记该漏拦族（不推荐：纳入范围漏拦按判级流程=必修）。

### Q10-3（LOW·误拦漂移，未登记）
`curl https://api.example/o <CFG>`、`wget …/O <CFG>` 类 r9 PASS → r10 **block**：_OUTPUT_FLAG_RE 新增 `[-/]o` 尾锚在 curl/wget 门上把"以 /o 或 /O 结尾的 URL token"认作输出旗标。F-9-3 声称范围是"cmd 版 sort /O"，负例必测只锁了 `-O URL` 横杠形，斜杠外溢面未声明非实测覆盖。修法一字符：斜杠形加 `(?:\s|^)` 词边界（仿 _COPY_T_RE）。

## 4. 腐化/长行/部署

- AST：handler/test 均 parse OK；>120 行 handler 0 条（test 715 行 125 字符——N3 口径仅约束 handler，合规）。
- 死代码：`_prev_command_word` 零调用（Q10-4：删或注释登记留用意向，随批处置，不独立立项）。
- 部署三处镜像（只读 sha256 前16）：src=main=architect=developer：handler `779ceb43ad7c9491`、__init__ `a0e39b0483c6b905`、plugin.yaml `59bc50cc0a50d233` **全一致**；工作树==HEAD（CRLF autocrlf 归一后 d253b58e092a386c 双向同）。✅

## 5. 裁决依据

立项三条件命中两条件：纳入范围新漏拦（Q10-1）+ 名实不符（Q10-1 声称句；附 Q10-3 纳入范围新误拦向）。Q10-2（§1 待补）、Q10-4（死函数/行数边缘）为 NOTES 随批。八项验收本身全绿、Q9-N2 修正句已名实相符——但 Q10-1 与上轮失实声称同型且伴真实漏拦，不能以 NOTES 放行。

**终裁：CHANGES REQUIRED**——最小批：Q10-1 命名目标 2 行支或登记翻转、Q10-1 声称句修正、Q10-3 词边界一行、Q10-2/4 随批。
