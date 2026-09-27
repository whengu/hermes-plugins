# review-011-sec：write-guard round11 终审（安全路，只读）

- 评审人：sa-0（安全路）｜日期：2026-09-22｜基线：git 94998f5（round11 FIX 闭环，工作区=HEAD 零脏改，handler.py sha16 65f7c1b4ff58f6ef）
- 判据：reviews/round11-context.md 收敛判据 + requirements/requirement-20260922-boundary.md。立项仅限纳入范围新旁路 / 纳入范围误拦 / 名实不符；排除范围与已登记边界一律附录。
- 入口口径：全部探针走 `on_pre_tool_call`（四守卫全链），无一例误用 _judge_terminal。
- 探针（本目录，载荷全文件内构造，命令行零载荷）：r11s_probe_a_fix_retest.py（F-10-1 三锁形×F-10-2 真输出标志形×回潮锁，r9/r10/r11 三代对照）、r11s_probe_b_bypass_fp.py（纳入范围新旁路搜寻：载体/链式/续行/邻域组合面）、r11s_probe_c_gendrift.py（round10 探针 a~h 全集形 harvest + r10 快照逐形代际 diff）、r11s_probe_e_newfaces.py（F-11-1/2/3/4 证据链 + 回潮锁对照）。
- 可运行性活证（真 pwsh 7 / curl 8.1.2，_r2tmp 草样，零受保护路径触碰）：`-Destination:<值>` 冒号绑定**可运行且真写**；`"-o"` 引号包选项 curl **真下载**；`-Destination=` 等号形 PS **拒绝**；全词粘连 `-Destination<值>` PS **拒绝**；引号包选项词 `-Destination` PS **拒绝**（佐证 TC-R11-17 非可运行形锁现状名实相符）。
- 真实链路活证二则：评审会话中含受保护路径字面量的 terminal 命令被用户批准层拒止；含删除命令词字面量的检索命令被守卫链实拦（拦截消息含命中模式）——防线在真实调用链生效。
- 部署一致性：源 + 主部署 + architect/developer 双镜像，__init__/handler/plugin.yaml 三文件 sha 全同代际（r10s_probe_0 复跑实测）。
- 基线独立复跑（非转述）：test_handler ALL PASS 29+4+309；_verify_r11 43/0、r10 46/0、r9 46/0、r8 30/0、r7 30/0、r5 28/0、r3 25/0；pm_verify_011 十六形全达标；handler AST OK、>120 行 0 条、TC-R11 计 17 条（与 fix-011 §4 声明逐项相符）。

## 一、F-10-1 / F-10-2 修复复测结论

| 项 | 攻击形复测 | 误拦/回潮复测 | 判定 |
|---|---|---|---|
| F-10-1 命名目标三锁形 | **锁形①前置命中**：`-Destination <CFG> 非保护`、Tee `-FilePath <CFG>`、守卫目录前置、小写混排、TAB 分隔、&&/管道/cd/; 链、sudo×pwsh 载体、单/双引号整词值、cmd 载体、`-dEsTiNaTiOn` 混排、Tee -Append 插位——**13 形全 approve**（r10 全 PASS 对照=本轮新封堵） | **锁形②反向源位**：`-Destination <WS> <CFG>`、反向×载体、`Tee <CFG> -FilePath WS`、位参前置 `<CFG> <BAK> -Destination WS`——全 PASS（r10 approve 对照=归正）；**锁形③双标志**：`-Container <CFG> -Destination BAK`、`-Path <CFG> -Destination BAK`、`-LiteralPath <CFG> -Destination BAK`——全 PASS（目标另有其主）。**Set-Content 出现即写不回潮**：裸形/-Path/-OutFile 别名/Add-Content/Out-File 管道全 block；尾位锁 n、cp/rsync/Get-Content 零行为差、引号标志不可运行形锁 PASS（pwsh 活证拒绝该形） | ✅修复成立（三锁形+不回潮全绿）。残余三面另立：冒号粘连 F-11-1、反序源位 F-11-3、缩写别名（附录①） |
| F-10-2 短形约束保持 | 真·输出标志形**全保持**：`-o` 独立 block、`-o` 空格等号 block、`-o` 粘连 block、cluster `-sSL -o ` 独立 block、`-sSL -o<粘连>` block、`/O` 独立 block、`/O` 粘连 block、`-o=` 等号 block、`--output`/`--output=`/`--output-document` block、`sort -o`/`/o` 小写 block、`CURL` 大写粘连 block——16 形零漏 | 归正向：sort `…/o`、`…/O`、curl/wget URL `…/o`、附录⑥ `my-dir-o`、home 内 `/o` 目录、`grep -o`、URL query 尾 o、`-oL` cluster、`mount -o` 全 PASS；`-O URL` 红线 PASS、`-z ts -O "URL"` 非 o 收尾不误伤、未知命令 `-o` 放行（Q-03 不变）、`-O` 两 URL 负例 PASS | ✅修复成立，约束不外溢。**但 cluster 尾 o+空格值形三代同漏**——见 F-11-4（非本轮引入，纳入范围新发现） |

代际漂移（探针 c，160 形全集两代实跑比对）：跨代差异仅 8 形，逐形核对**全部落在 F-10-1/F-10-2 预期翻转面**（前置封堵×3、反向归正×2、误拦归正×3）；其余 152 形零漂移。round10 探针 a~h 复跑：c/e/f/g/h 全绿零 DIFF；a 的 1 处、d 的 5 处 DIFF 逐条核为探针侧 r9-era 预期值与登记边界（glob/非可运行形/$HOME）之差，非 handler 回退——与 round10 §四附录、TC-R11-17、本轮 pwsh 活证三方一致。

## 二、发现（全部实测复现；r9/r10/r11 三代对照见探针 a/e 输出行）

### F-11-1（LOW·纳入范围新旁路）PS 命名目标「冒号粘连形」`-Destination:<值>` 收集门未收

- 复现：`Copy-Item -Destination:<CFG> <非保护>`、`Tee-Object -FilePath:<CFG> -InputObject x`、`-Destination:'<CFG>'`（引号值）→ **三代全 PASS**。真 pwsh 活证该形可运行且完成写入（pd_colon.txt 生成）。
- 判据：boundary §纳入4「常规选项粘连」（`--target-directory=<dir>` 同款分隔符粘连）×§纳入7；冒号是 PowerShell 原生参数绑定分隔符（文档语法，非冷知识层；`-o<file>` 粘连有 S-1 HIGH 先例、`--target-directory=` 有 C3 先例）。round11 新建命名目标支的同面直接漏。
- 根因：token `-Destination:D:/…/config.yaml` 整token 归一化后不匹配受保护谓词，**上游收集门 L956 就未收**，命名支根本没有判定机会——与 S-1 当时 `_GLUED_O_RE` 提取先例同构。
- 修法方向（≤4 行，比照 _GLUED_T_RE/_GLUED_O_RE 提取位 + 收集门一处 elif）：新正则 `^-(?:Destination|FilePath)[:](\S+)$`（IGNORECASE），提取值段送 norm；写判定沿用命名支语义（本 token 即绑定值）。等号形 `-Destination=`/全词粘连 `-Destination<值>` 经活证 PS 均拒绝，非可运行形不入本支（附录②）。

### F-11-2（LOW·纳入范围新旁路）引号包输出选项词 `curl "-o" <CFG>`（纳入3 明文面）

- 复现：`curl "-o" <CFG> http://x`、`curl '-o' <CFG>`、`curl "--output" <CFG>` → **三代全 PASS**。curl 8.1.2 活证：shell 剥引号后与裸 `-o` 完全同义，真写目标文件。
- 判据：boundary §纳入3 逐字命中——「整词引号形：包裹路径、**选项**（如 `cp '-t' <dir> x`）」，示例即引号包选项词；`_COPY_T_QUOTED_RE`/F-7-2 是本口径在 -t 面的既有落地先例，-o 族同义务未覆盖。§纳入1 明列 curl -o 必防。
- 根因：`_OUTPUT_FLAG_RE` 短形约束要求 `[-/]o` 前随空白/段首，`"` 阻断 lookbehind；`_OUTPUT_FLAG_EQ_RE`/`_GLUED_O_RE` 亦不吃引号 token。
- 修法方向（≤3 行，_COPY_T_QUOTED_RE 同款）：`_OUTPUT_QUOTED_RE = re.compile(r"[\x27\x22](?:-{1,2}[oO]|--output(?:-document)?)?[\x27\x22]\s*$", …)` 并入 `_OUTPUT_FLAG_RE.search(before) or …` 判定式（保留引号成对整词，不做通用引号剥离——F-7-2 禁令不回潮）。

### F-11-3（LOW·纳入范围误拦）命名支绑定词表含**源参数**，反序双标志形源位再误弹

- 复现：`Copy-Item -Destination <WS> -Path <CFG>` 与 `-Destination <WS> -LiteralPath <CFG>` → **approve**。pwsh 活证：该形目标=WS（非保护），CFG 实为**源**（`-Path`/`-LiteralPath` 是 Copy-Item 源参，非目标参）——源位读被弹卡，违 round11-context §30 锁形精神与 fix-011-input §32「CFG 是源→必须 PASS」红线同族。
- 三代对照：r10=approve（F-10-1 反向误弹同源、修复令内明列该向）、r11 仍 approve——**修复不彻底面**（命名支对 before 尾锚 `-Path`/`-LiteralPath` 也判写）。根因：`_PS_NAMED_TARGET_RE` 五词表把源参数 Path/Container/LiteralPath 与目标参数 Destination/FilePath 并列作「命名**目标**」绑定判据，名实不符（PS 语义：Copy-Item 目标仅 Destination；Tee-Object 目标仅 FilePath；Path/LiteralPath 恒为源、Container 非该族目标词）。
- 判据：boundary §纳入7 只义务拦「写目标=配置」；源位弹卡属纳入范围误拦（F-9-1/F-10-1 反向同判例）。
- 修法方向（≤2 行）：前置写绑定判据收窄为 `-(?:Destination|FilePath)\s*$`（目标词专用尾锚正则，或给现正则按 cmd 分词表）；`_PS_NAMED_ANY_RE` 五词表**不动**（末位否决仍需要 Path/LiteralPath 在场信号）。负例：`-Path <CFG> -Destination <WS>`（CFG 源位）保持 PASS 零差；`-Destination <CFG> …` 封堵形零差。

### F-11-4（MED·纳入范围新旁路）o 收尾 cluster + 空格值 `curl -so <CFG>`（S-1 家族残面）

- 复现：`curl -so <CFG> http://x`、`curl -sSLfo <CFG> http://x`、`wget -qO <CFG>`、`sort -ro <CFG> d.txt` → **三代全 PASS**。curl 活证：getopt cluster `-so` 尾 o 带独立值 = `-o <CFG>` 完全同义，真写文件（r11_c_so.txt 实际下载成功）。
- 判据：boundary §纳入4「常规选项粘连 `-o<file>`」+§纳入1「curl -o」；`-sSL -o` 与 `-o<粘连>` 两向已被 S-1/round10 封住，**cluster 内含 o + 分离值**是同一 getopt 语义的第三种写法，真实 agent 高频（-sfo/-qO/-sLfo 是常规日志/静默组合），非冷知识。
- 根因：r11 `_OUTPUT_FLAG_RE` 短形 `(?:^|(?<=\s))[-/]o\s*(?:=\s*)?$` 要求 `-o` 整 token 独立；`_GLUED_O_RE` 要求值粘连进 token；`-so <CFG>` 两不沾。
- 修法方向（≤3 行，与 F-10-2 同点收敛不冲突）：短形组并一条 dash 专属 cluster 尾 o 支 `(?:^|(?<=\s))-{1,2}[a-zA-Z]*o(?:\s*=\s*)?$`（**斜杠方言不参与**——cmd 无 cluster 语义，`ws/o` 类归正成果不回潮）；误拦向必测 `curl -so <非保护>`、`grep -o`（门外命令）、`mount -o`（门内词不含 curl/wget/sort 者不变）。F-10-2 四归正形 + `sort ws/o` 族在回归锁内复跑。
- 分级说明：列 MED 因 curl/wget/sort 三入门命令全覆盖、单命令直写配置文件、修法复用现成正则单点（灰区判据「5 行内可修不引入新解析层」通过）；系既有面（三代同陷），非 round11 引入。

## 三、红线保持核查（全部实测，on_pre_tool_call 正确入口）

1. **gateway restart block 含续行** ✅ 12 形：restart/run/start、大写、bs+LF、bs+CRLF、跨行续、全局 flag、sudo/&/cmd 载体交叉、内嵌引号体全 block；**status/stop/--help 不误伤** ✅ 3 形 PASS（r10s_probe_d 在 r11 现行 handler 复跑 47/52 ok，5 处 DIFF 全为探针侧登记边界预期差，§一已逐条核）。
2. **rm -r 平台分层** ✅：rm -r 守卫目录、rm -rf home、rd /s /q 全 PASS（不扩，拦截职责在平台 approvals 层，与 CHANGELOG 分层登记一致）。
3. **cp 写配置弹卡** ✅ 不回潮：直写/引号源/copy /Y/cmd 裸形/Copy-Item 目标/sudo bash -c 六形全 approve；cp 源位/Get-Content 读/mv 族 PASS；Set-Content/Add-Content/Out-File 出现即写 block；write_file/patch/memory/read_file 入口 7 形全绿。
4. F-9-1 复制族源位读红线不回潮 ✅（`Copy-Item <CFG> <BAK>`、`cp <CFG> <BAK>`、rsync 源位、双标志源位全 PASS）。

## 四、附录：排除范围/登记边界实测罗列（一律不立项）

1. PS **唯一前缀缩写**词形 `-Dest <CFG>`、`-PsPath`、`-OutFile`（Set-Content 面已 block）：缩写解析属 PS 词法冷知识（比照 S-2 别名 cp/tee 登记同族），两代同向——登记不立项（-Dest 尾位形经末位启发仍 approve，非零兜底）。
2. **非可运行形**（pwsh 活证拒绝）：`-Destination=<值>`、全词粘连 `-Destination<值>`、引号包选项词 `'-Destination'`（TC-R11-17 现获活证背书）→ 附录④先例维持。
3. `backtick+LF` PS 续行：排除2 反斜杠奇偶/续行族既登记（fix-008 同型），PASS 两代同向。
4. 三层嵌套 `sudo bash -c "pwsh -Command \"…\""` → PASS：排除4 多解释器嵌套；两嵌套 bash×pwsh 组合实测**命中**（approve），纳入5 义务达成。
5. glob 目标（home/*.yaml、守卫/*.py）approve 弹卡：C4 保守既有登记；`$HOME` 未展开、`sc` 别名、`-O` 受保护 URL 位 block（保守向）：既登记。
6. `-Destination <CFG> <WS> <BAK>` 数组化多值形：实 shell 参数绑定歧义/非常规，r11=approve 保守弹卡非静默——现状锁附录。
7. 探针 a/d 的 6 处 DIFF 行系探针侧 r9-era want 与登记边界之差（§一），非 handler 行为漂移；r10s_probe_b 2 处（cw=root 登记边界、引号包载体附录③）维持。

## 五、名实核查

- fix-011.md §1~§4、CHANGELOG round11 节、round11-context 验收基线**逐项复跑相符**：三锁形断言、16 形翻转、Set-Content 不回潮、_prev_command_word 0 残留（grep 实测）、改动纪律（git diff 2cc28cf..HEAD：命名支 3 逻辑行+末位否决 1 续行 ≤5；短形约束 1 正则行 ≤3；无顺手改）、Q10-1 失实句修正句在位——**该批声明未发现名实不符**。
- 唯二窄差（随 F-11 批处置，不单列）：①fix-011-input §21 词表把 Path/Container/LiteralPath 命名为「命名**目标**」标志，PS 语义系源参/非目标参——正则名与语义名实差，根因已入 F-11-3；②TC 计数 17 条与「≥12」规格相符无违。

## 六、裁决

**CHANGES REQUIRED** —— 4 条（全实测+活证，三代对照定位，全过灰区≤5行判据）：**F-11-1**（LOW）PS 命名目标冒号粘连形 `-Destination:<CFG>` 收集门未收，pwsh 活证可写；**F-11-2**（LOW）引号包输出选项词 `curl "-o" <CFG>` 三代漏，纳入3 明文义务面；**F-11-3**（LOW）命名支绑定词表含源参，`-Destination <WS> -Path <CFG>` 源位再误弹（修复不彻底+词表名实差）；**F-11-4**（MED）o 收尾 cluster+空格值 `curl -so <CFG>` 三代漏，curl 活证真写，纳入1×纳入4 同族残面。修复复测本体：F-10-1 三锁形/不回潮、F-10-2 保持/归正**全部达成**，代际 160 形漂移零意外；三条红线全保持；基线 29+4+309 / 43+46+46+30+30+28+25 + pm 十六形独立复跑全绿；部署四目标同代际；附录 7 族不立项。

—— sa-0（安全路）2026-09-22 round11 终审，全程只读；探针 r11s_probe_a/b/c/e + 代际快照 handler_r10commit.py（2cc28cf）/handler_r9_cbd6301.py 复用，活证草样全落 _r2tmp。
