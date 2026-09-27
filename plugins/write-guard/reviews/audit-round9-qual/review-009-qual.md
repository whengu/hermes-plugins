# review-009-qual：round9 终审·质量路（只读）

- 评审对象：workspace/write-guard @ cbd6301（round9 FIX 闭环，handler.py S-1~S-5）
- 评审方式：全部实跑（测试/verify/探针/sha），零改码（只读；探针脚本落本目录）
- 探针：`reviews/audit-round9-qual/q9_cw_probe.py`（84+ 例，_command_word 新旧对拍含独立复刻旧实现）
- **裁决：PASS_WITH_NOTES**（NOTES 六条，均不涉 handler 回改必要；两条建议登记边界句）

## 1 验收实跑（全绿，与基线一致）

| 命令 | 末行 | 对基线 |
|---|---|---|
| `python test_handler.py` | ALL PASS (29 scan cases + 4 hook cases + 277 new cases) | ✓ 29+4+277 |
| `python _verify_r9.py` | 通过 46 失败 0 [] | ✓ 46/0 |
| `python _verify_r8.py` | 通过 30 失败 0 [] | ✓ 无回潮 |
| `python _verify_r7.py` | 通过 30 失败 0 [] | ✓ |
| `python _verify_r5.py` | 通过 28 失败 0 [] | ✓ |
| `python _verify_r3.py` | 通过 25 失败 0 [] | ✓ |
| `python reviews/fix009-scratch/pm_verify_009.py` | S-1~S-5 全 approve/命中方向，NEG 行 PASS 保持 | ✓ 与 round9-context 声称一致 |

TC-R9 块 27 条逐条 OK（含 N1 锁向 26/27）。

## 2 五项改动名实对读（注释/文档声称 vs 实测）

### S-1 `_GLUED_O_RE`（L266）
声称：仿 _GLUED_T_RE 粘连提取；`(?!=)` 排除 = 形（已有 _OUTPUT_FLAG_EQ_RE）；双 dash 天然不匹；门=curl/wget/sort（未知命令维持 MED-2 放行）。
实测：C 组 7 claims 全符；`curl -oCFG`/`-sSL -oHD`/`sort -o`/`wget -O` → block；`-O URL`/`-oL`/`-o 空格`/`--output=`/`grep|tar|dd|python -o` 红线零回退。**名实相符**。
附加行为（未言但同构合理）：多 o cluster（-boO/-oo/-zot）剥值进归一——与 _GLUED_T_RE 同款语义，且仍在门内，无新 FP 证据。

### S-2 `_PS_WRITE_RE`（L256）
声称：+Copy-Item|Tee-Object；别名 cp/tee 不扩（登记不修）。
实测：词表恰 5 词，`cp`/`tee`/`Get-Content` 确不在表（\b 对 CopyItem/Copy-To 无误命中）；`pwsh -Command "cp evil CFG"` 经既有 shell 链仍 approve（_verify_r9 双锁真）。**名实相符**。

### S-3 单 `&` 分段（L822）
声称：&&/|| 长度降序先消费；引号感知 URL 内 & 不误切；`2>&1> CFG` 残段仍 block（重定向分支独立识别成立，"不扩则登记"分支未触发）。
实测：F 组 12 例全对——单/双引号 URL & 不分段、`>&2`/`2>&1` 不裂、`echo x 2>&1 > CFG` 与 `> CFG&dir` 均 block、`start /b a&b CFG`、`echo a&&b&echo c` 等 PASS。**三文档（fix-009/CHANGELOG/context）"未登记残段边界"口径与实测一致**。

### S-4 `_command_word` 重写（L614）——本轮最高风险项，独立 ≥30 例回归
声称：循环剔除 wrapper(sudo|time|env|nohup|runas)+环境赋值+首位前连续选项词；全剔→None；零新解析层；不改矩阵其他逻辑。
实测（新旧对拍）：
- **误拦面=零**（任务点名形态全过）：findstr /c:"a b"、git -C、git -c、cut -f1 -d:、tail -n、sed -n、grep -r、chmod、diff、wc、tr <、head -c、tar czf、引号命令词 "cp"/'echo'、管道纯读、cd 链（含 cd 不跨管道）——命令词提取与旧实现逐 token 一致（24 例仅 2 例差异，见下）；端到端方向全保持放行。
- 正向 8 例（sudo/runas /user:/nohup/LANG=C/time/env FOO=1 前缀 cp→approve、sudo truncate→block、sudo -u root 登记边界→PASS）全对。
- 触及面差异 1 例（**Q9-N1**）：以 `/` 开头的 POSIX 绝对路径命令词被当选项词跳过——`/usr/local/bin/ls cp <home配置>` 旧=PASS，新 cw='cp'→**approve（新增弹卡形 FP）**；`/bin/cp evil <GUARD>` 方向不变（旧亦不在复制族→PASS，无回潮）。形态 exotic（三巧合叠加），弹卡保守方向，建议登记边界。
- 注释"仅剔除链中消费/矩阵其他逻辑未动"经 diff 核实为真（git diff 仅函数体+2 常量）。

### S-5 `_BARE_CARRIER_RE` 递归（L325/L874）
声称：载体词 8 族+连续开关位 `[/-][A-Za-z]\w*`+引号体不成立时 rest 以 depth+1 递归，受 _NEST_DEPTH_LIMIT=3 门；引号体既有分支零回归。
实测：cmd //q //c、pwsh -Command、sh -c 裸形全命中；`cmd /c "…"`/`bash -lc '…'` 引号体分支不回潮；cmd //c dir、Get-Date、非保护 copy 放行；三层套壳 approve、四层 PASS（深度门实证）；BARE↔EMBED 互斥门实测成立（引号体段 BARE 虽 match 但被 `EMBED.search is None` 条件挡下，名实相符）。
发现（**Q9-N2**）：双横杠/带值开关打断识别——`bash --login -c "cp evil GUARD"`、`pwsh -Version 7 -Command "…"` → PASS（漏拦方向）。系 EMBED 既有同族限制（round8 基线亦如此，非 S-5 引入），S-5 未言此限制，建议接受边界补一句。

## 3 三文档互洽 + N1~N5 复核

- CHANGELOG round9 节 / fix-009.md / round9-context.md：五项描述、验收数字（277/46/30/30/28/25）、登记边界（sudo 带值形、PS 别名）、S-3 残段处置——**三处口径互洽，与实测一致**。
- **N1 锁向句改回=名实基本相符**：round8 总括句已改"round9 TC-R9-26/27 已补锁，登记闭环"，两锁实测方向正确（半混劈 tdir= 变体锁 PASS、F-7-3 整词 -t 锁 approve）。微疵 Q9-N4：TC-R9-26 标题含"tdir="但载荷为 `cp --"target-directory"=GUARD`（同族不同字面）。
- N2（数量词 3 替换/2 调用点）round8 节保持 ✓；N3 阈值句在，round9"新增行最长 ≤120"实测 max=114 ✓。
- **N4 sha 声称现场核实为真**：pipeline-status"round7 代际 handler sha=c1b3ddb0"——90de321 blob 按磁盘 CRLF 行尾还原 sha256 前缀=c1b3ddb0 ✓（LF 原值 fd3f1423，deploy.py 保 CRLF，口径自洽）。
- N5 heredoc 登记锚：boundary §排除3 括注已落地（be14c7f diff 实证）✓。
- Q9-N5：fix-009.md/CHANGELOG 末句"未 commit、未 deploy"为过程时点记录，现状已 cbd6301+部署——修订史文档宜补一行收口；pipeline-status 无 round9 行（PM 收尾事项）。

## 4 静态/腐化/部署镜像（只读）

- AST：handler/test/5 个 _verify/deploy 全 parse OK；无重复函数定义；模块级正则无未引用死符号；无 TODO/FIXME/print 残留。
- 长行：handler.py >120 = **0 行**（max 114）；test_handler L437/544=120（压线合规）、L715=125 为 round8 前既有（N3 口径注明 test 不强制，但本轮 diff 新增区无 >120 行）。
- 部署镜像 sha256：工作区 handler=部署主=architect 镜像=developer 镜像=`36ebee2c26cf…`（四份全等）= git HEAD blob CRLF 还原 ✓——**round9-context"部署同代际"声称成立**。
- 工作区 git status 干净（仅本报告目录为本次评审新增，只读纪律未触被测文件）。

## 5 NOTES 汇总（均不阻断收敛）

| # | 级 | 条目 | 建议 |
|---|---|---|---|
| Q9-N1 | 行为微面 | _command_word 把 `/` 开头绝对路径命令词当选项剔除：`/usr/local/bin/ls cp <home路径>` 新增 approve 形 FP（漏拦面无回潮） | 登记边界，或限定剔除仅对"恰为 -x/单一 /x 选项形"生效（3 行内） |
| Q9-N2 | 既有面延伸 | `bash --login -c "…"`/`pwsh -Version 7 -Command "…"` 双横杠/带值开关打断 EMBED+BARE→PASS（round8 基线同款） | CHANGELOG 接受边界补一句 |
| Q9-N3 | 文档疵 | CHANGELOG round9"红线执行：每项 ≤6 行"对 S-4（3 常量+7 行体）/S-5（5+7 行）不严格，fix-009.md 如实记 5+7 | 总括句改"每项 ≤6 行（S-4/S-5 为常量+体合计 ≤~12 行）" |
| Q9-N4 | 措辞疵 | TC-R9-26 标题"tdir= 变体"与载荷 `--"target-directory"=` 字面不吻合（方向锁正确） | 补注或换载荷 |
| Q9-N5 | 文档滞后 | "未 commit/未 deploy"句现状失实（已 cbd6301+部署 36ebee2c）；pipeline-status 缺 round9 行 | PM 收尾批注 |
| Q9-N6 | 核实通过 | N4 c1b3ddb0 声称现场为真；部署四镜像=HEAD 一致；N1 改回句实质闭环 | — |

**收敛判定**：纳入范围内零回潮、验收全绿、五项名实与实测一致（两处措辞级夸大），NOTES 不涉 handler 逻辑回改必要 → 质量路 **PASS_WITH_NOTES**。Q9-N1/N2 两条建议由 PM 并入下批文档登记（若动 _command_word 需走灰区 ≤5 行标准）。
