# review-012-sec：write-guard round12 终审（安全路，只读）

- 评审人：sa-0（安全路）｜日期：2026-09-23｜基线：git **4e254c8**（round12 FIX 闭环；PM 带外更正 sha，现场 `git log --oneline` 自证；上代对照 **94998f5**）。工作区 handler.py/test_handler.py 与 4e254c8 **逐字节零差**（审查期间 HEAD 前进两枚 PM 纯文档提交 78bf197/8dde55e——X-13 立项候选预研+curl `=` 形活证甄别，与本审计 §三 F-12-1/2、附录 1 独立结论互为印证，代码面未动）。
- 判据：reviews/round12-context.md 收敛判据 + requirements/requirement-20260922-boundary.md。立项仅限纳入范围内新旁路 / 纳入范围内误拦 / 名实不符；排除范围与已登记边界一律附录。
- 入口口径：全部探针走 `on_pre_tool_call`（四守卫全链），无一例误用 _judge_terminal。
- 探针（本目录，载荷全文件内构造，三代对照 new/r11(94998f5)/r10）：r12s_probe_a_fix_retest.py（F-11-1~4 逐改动双向差分 69 形：封堵+误拦，PM 指定邻域全覆盖）、r12s_probe_b_bypass_fp.py（改动邻域新旁路搜寻 + PM 转来 X-13-1/X-13-2 独立复核）、r12s_probe_c_gendrift.py（round11 探针 a/b/e 实跑 harvest + rerun 日志 + pm011/012 表 + TC 字面量 + 本轮 a/b 新形，共 **304 形** new×r11 逐形代际 diff）、r12s_probe_d_redlines_variants.py（红线四形 + 处置分流 + 引号粘连变体三代）。
- 可运行性活证（真 pwsh 7 / curl 8.1.2，草样全落 _r2tmp/r12s，零受保护路径触碰）：①`Copy-Item -Destination <dst> -Path <src>` 组合**可运行且真写入 Destination**（dstx.txt 生成）；②`Tee-Object -LiteralPath <f>` **文件真实写出**（teeout.txt 生成）——PM 活证独立复核成立；③`curl -sfo=X` 实际写入文件名字面 **`=X`**（产物 `=live_laplace.bin`）——短选项族 `=` 非分隔符，cluster×等号形为**非等价形**（附录）；④`curl "-o<v>"`/`"-so<v>"` 引号包整词粘连**真写**（qglue.bin/qso2.bin 生成）→ F-12-3；⑤`Copy-Item "-Destination:x"` 引号包整词 PS 拒绝（Cannot find drive）→ 非可运行形锁现状正确。
- 真实链路活证：本轮评审会话中一条含 `/tmp` 的 terminal 命令被部署代守卫**实拦**（防线在真实调用链生效，非仅内存探针）。
- 部署一致性：源+主部署+architect/developer 双镜像，__init__/handler/plugin.yaml 三文件 sha 全同代际（r10s_probe_0 复跑实测）。
- 基线独立复跑（非转述）：test_handler ALL PASS **29+4+329**；_verify_r12 53/0、r11 43/0、r10 46/0、r9 46/0、r8 30/0、r7 30/0、r5 28/0、r3 25/0；pm_verify_012 **23 形全达期望**；pm_verify_011 **十六行零回退**；handler AST OK、>120 行 0 条、TC-R12 计 20 条（与 fix-012 §6/round12-context 声明逐项相符）。

## 一、F-11-1~4 修复复测双向差分（探针 a/d）

| 项 | 封堵向复测 | 误拦向复测（PM 指定邻域） | 判定 |
|---|---|---|---|
| F-11-1 冒号粘连 | `-Destination:<CFG>`、`-FilePath:<CFG>`、单/双引号值、混排 `-dEsTiNaTiOn:`、pwsh 载体内嵌、守卫源码目标——8 形全命中（r11 全 PASS 对照=本轮新封堵） | 等号形 a4/引号包选项词 a9（pwsh 活证拒绝）PASS 不回潮；**值含 dash** `-Destination:"-x"`/裸 `-Destination:-x` PASS（不吞后续 token 为源位形）；目标非保护值 PASS；冒号形×后随标志否决、冒号×反向源位 PASS | ✅修复成立（**但残留半截**：后随源参标志形仍 PASS，见 F-12-2） |
| F-11-2 引号选项词 | `curl "-o"`/`'-o'`/`"--output"`/`"--output-document"`、`wget "-O"`、`sort "-o"` 全 block；引号包粘连值 `-o<CFG>`（值段在引号内）不误扩 | grep 门外、`curl "-O" <url>` 红线、`"-o" <非保护>`、任意引号 token（`"header: X"`）全 PASS；`-o` 在引号体中间不成词 PASS | ✅修复成立（PM 修正 sa-0 可选组缺陷逐字符落地）。**引号包「选项+粘连值」整词组合仍漏**——F-12-3 |
| F-11-3 收窄 | c4 `-Destination <CFG> 非保护`、c6 Tee、守卫源码、TAB、引号整词值等封堵零回退 | c1/c2/c5 源位误弹全归正 PASS；**PS 三向锁形零回退**：前置封堵✓（c4/c6/n3/n4）反向源位✓（c3/B/B2/n1/n2）双标志否决✓——三向 12 形全符 r11 锁形 | ✅修复成立。**但收窄引入 Tee -LiteralPath 目标丢失回退**——F-12-1（探针 c 代际差异实锤 approve→PASS×2） |
| F-11-4 cluster 尾 o | `-so`/`-sSLfo`/`-qO`/`-ro`/`-fo` 全 block；bash -c 内嵌递归保持 | **`--http1.0` 数字尾 PASS**（`[a-zA-Z]*` 不吃数字）；`-o=` 裸等号、`-O` 大写红线、`-sSO`、grep/mount 门外、`ws/o`、URL 尾 `/o`、`pro-o`、`my-dir-o`、`-o` 带值参干扰、未知命令——误拦邻域 13 形全 PASS；`-so=CFG` 等号×cluster 系非等价形（活证③）PASS 归附录 | ✅修复成立，外溢零。**`echo curl -so <CFG>` 并入既有一揽子误拦族**（见附录 3） |

复测本体 69 形终态 69/69（4 处初判 DIFF 均核为我方预期误差：复制族处置=approve 弹卡（B3 分流）、curl `-O <CFG>` 登记保守族、`-sSO` 同族、`-sfo=` 非等价形——已以活证/登记背书修正探针）。

## 二、代际漂移（探针 c：304 形两代实跑）

33 处差异逐行核对：F-11 预期翻转 26 形（冒号×8、引号选项×6、cluster×5、收窄归正×3、内嵌×1、`-dEsTiNaTiOn:` 混排自然覆盖×1、`-LiteralPath <CFG> <位参目标>` Q-11-1 同根归正×1——后两条系翻转族标记正则欠列，非预期外）；同族保守/既有面 4 形（`-fo` 真写新封堵、`-sSO`、echo 族，附录 3）；**预期外回退仅 2 形 = Tee-Object `-LiteralPath` 两向 approve→PASS**——立 F-12-1。其余 271 形零漂移。

## 三、发现（全部实测复现；与 PM fix013-scratch/pm_probe_013_pre.md 候选合并定级）

### F-12-1（MED·本轮改动引入回退·纳入范围新旁路）Tee-Object `-LiteralPath` 目标语义被全局词表压平丢失【= PM X-13-2，独立复核+活证成立】

- 复现：`Tee-Object -LiteralPath <CFG>`（末位）、`Tee-Object -LiteralPath <CFG> -InputObject x`（前置）→ new=**PASS**（r11=approve，探针 c 实锤为本轮唯一预期外回退）。pwsh 活证：`Tee-Object -LiteralPath <f>` **文件真实写出**。
- 判据：boundary §纳入7（写目标=home 内配置）+§纳入6（同语义必防）。PS 语义 Tee-Object 的 `-LiteralPath` 属 `-FilePath` 参数集（即输出目标），与 Copy-Item 的 `-LiteralPath`（源参）**语义相反**。round12 改动 1 把 TARGET 收窄为 cmd 无关的全局 {Destination,FilePath}，将 per-cmd 语义压平——F-11-3 的正确修复以牺牲 Tee 面为代价（fix-011 §词表原名实差的第二次发作：词表模型不分 cmd）。
- 修法方向（≤3 行）：TARGET 判定按 cmd 分表（copy-item:{Destination}；tee-object:{FilePath,LiteralPath}）；`_GLUED_NAMED_RE` 词集同步分 cmd。锁形保全清单：本表 T1/T2/T4/T5 + X4/X5 + TC-R11/R12 全量。

### F-12-2（MED·纳入范围新旁路·F-11-1/F-11-3 修复残留面）命名支「后随任意命名标志→目标另有其主」否决过宽【= PM X-13-1，独立复核+活证成立】

- 复现：`Copy-Item -Destination <CFG> -Path <WS>`、`… -LiteralPath <WS>`、冒号形 `Copy-Item -Destination:<CFG> -Path <WS>` → **PASS**（r11/r10 同漏=三代同陷，但属收敛判据内「纳入范围内新旁路」且直接使本轮 F-11-1 修复只成半截）。pwsh 活证：`-Destination <dst> -Path <src>` 组合合法运行且**真写入 Destination**——CFG 是写目标，非「目标另有其主」。
- 根因：前置支末位否决 `not _PS_NAMED_ANY_RE.search(seg[m.end():])` 把「后随**任意**命名标志」都当作目标移交信号——该假设只对「后随标志为本 cmd 目标词」成立（锁形 B 语义）；后随源参标志（Path/LiteralPath 于 Copy-Item）时真目标已绑，否决不应生效。PM 探针侧根因推演（before(ws) 尾锚 TARGET 因 Path 移出而失效 → 前置/末位两支双拒）经复核成立。
- 判据：§纳入7 直写配置旁路；修法 ≤4 行（否决条件精确化为「后随目标词标志才移交」，与 F-12-1 同根合并为 per-cmd 目标表一次修）——灰区判据通过。
- 邻界核正（不扩面）：X5 `-Recurse`（非命名标志）approve 正确；T2b `-LiteralPath CFG -FilePath WS` 双目标竞绑属绑定歧义形附录 4；`-Destination CFG -ToDouble -Path WS` 双标志介入同理由本条覆盖。

### F-12-3（LOW·纳入范围新旁路）引号包「选项词+粘连值」整词形 `curl "-so<CFG>"` / `"-o<CFG>"`（纳入3×纳入4 组合面）

- 复现：`curl "-o<CFG>"`、`curl '-o<CFG>'`、`curl "-so<CFG>"` → **三代全 PASS**。curl 8.1.2 活证：shell 剥外层引号后与裸 `-o<CFG>`/`-so <CFG>` 完全同义，真写目标文件（qglue.bin/qso2.bin 生成，内容=载荷）。
- 判据：boundary §纳入3「整词引号形：包裹路径、**选项**」×§纳入4「常规选项粘连 `-o<file>`」两明文条款的组合面——F-11-2 收了「引号包选项 + 空格值」，`_GLUED_O_RE` 收了「裸粘连」，**组合形**是同类腐化（F-7-2 先例：`'--target-directory'=…` 引号粘连组合曾判 MED 修复，口径同源）。
- 根因：token 以引号起始，`_GLUED_O_RE`/`_GLUED_T_RE` 的 `^[-/]` 不吃；`_OUTPUT_QUOTED_RE` 整词内容限「仅选项词」（PM 修正后的正确约束）不再含值段——但「引号内=选项词+值」剥引号后仍是可运行同义形。
- 修法方向（≤2 行）：`_OUTPUT_QUOTED_RE` 内容段并一条「选项词后随非空白值段」支（`(?:[-oO|--output…]<值)` 提取值段，比照 `_GLUED_NAMED_RE` 引号值处理），或于收集门对整词剥外层引号后重入 `_GLUED_O_RE`——仍禁通用引号剥离（F-7-2 禁令不回潮）。必测误拦向：`grep "-o<v>"` 门外、`curl "-O<v>" URL` 语义、引号穿插半混形 `-o"<v>"` 保持附录（排除1）。

### 名实核查：无违

fix-012 §0 表 23 形、§1~§6、round12-context 验收基线逐项独立复跑**全相符**（探针 a + pm012/011 + 8 个 verify 全绿）；改动行数界内（判定式重排括号形语义不变已在制品注明）；根因链登记如实（五词表出自 fix-011-input 并列错误）。NOTES 两项（fix-011 [DONE]、TC 笔误按实一处）核见在位。

## 四、红线四形保持核查（探针 d 全实测）

1. **gateway block**：restart/bs+LF 续行/sudo bash -c 载体交叉全 block；status 不误伤 ✅。2. **cp 配置弹卡**：cp/Copy-Item 目标配置 approve；守卫源码复制族=弹卡向（B3 分流一致）✅。3. **Copy-Item 源位 PASS**：`<CFG> <BAK>`、`-Path <CFG> <BAK>`（本轮归正）✅。4. **rm -r 分层**：rm -rf home、rd /s /q 不扩 ✅。处置分流：冒号粘连写配置=approve、curl -o 族（含引号选项词形）写守卫源码=block ✅。

## 五、附录：排除范围/登记边界实测罗列（一律不立项）

1. `curl -sfo=<CFG>` 等 cluster×等号形：**活证非等价**（写文件名含 `=` 前缀，不覆写 CFG）——与 `-Destination=` 同归「非可运行/非等价形」附录族；裸 `-o=` 既有 block 为 r10 保守锁不回退。
2. `curl "-o"=<CFG>`、引号穿插 `-'o'<v>`、整词粘连 `"…"` 无尾随值（pwsh 活证拒绝）——排除1 引号穿插族。
3. `echo curl -so <CFG>` block：round2 建议-2（命令名 `search(before)` 全文搜）既有同族误拦（`echo curl -o <CFG>` r2 起即 block），本轮 cluster 支仅扩量不变质，fail-closed 向——随建议-2 一并处置，不单独立项；`-sSO <受保护URL>` 保守族（round11 附录 5 既登记）同列。
4. `Tee-Object -LiteralPath <CFG> -FilePath <CFG2>` 双目标竞绑：PS 参数集冲突歧义形，PASS 现状锁。
5. `-Destination:""` 空值交叉、缩写别名族（round11 附录 1）、backtick 续行、三层嵌套、glob 目标——既登记零变化。

## 六、裁决

**CHANGES REQUIRED** —— 3 条（全实测+活证；F-12-1 系本轮改动引入回退=「每轮修复引入新回归」规律第 5 次应验；F-12-1/2 与 PM 候选 X-13-1/2 合并同根登记：PS 命名参数语义 per-cmd，判定层全局压平）：**F-12-1**（MED）Tee `-LiteralPath` 目标语义被 TARGET 收窄丢失，pwsh 活证真写出；**F-12-2**（MED）命名支后随源参标志一票否决过宽，`-Destination <CFG> -Path <WS>`（含冒号形）真写入旁路，pwsh 活证；**F-12-3**（LOW）引号包「选项+粘连值」整词 `curl "-so<CFG>"` 三代漏，curl 活证真写，纳入3×纳入4 组合义务面。修复复测本体：F-11-1~4 全达成、69 形双向差分终态全绿、PM 指定邻域零误拦、PS 三向锁形 12 形零回退、红线四形+分流全保持、基线 29+4+329 / 8 verify + pm 两套独立复跑全绿、304 形代际漂移除 F-12-1 外全落预期面、部署四目标同代际、名实相符、附录 5 族不立项。

—— sa-0（安全路）2026-09-23 round12 终审，全程只读；探针 r12s_probe_a/b/c/d + 代际快照 _r2tmp/handler_r11_94998f5.py（94998f5），活证草样全落 _r2tmp/r12s。
