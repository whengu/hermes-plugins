# Round13 质量路独立终审报告（sa-1 / review-013-qual）

- 评审人：sa-1（质量路）｜日期：2026-09-23｜基线：git **10a2094**（round13 修复闭环；
  HEAD 之后仅两枚纯文档提交 5de6694/1db11bb，代码面零差——`git diff 10a2094 HEAD -- handler.py test_handler.py` 为空，实核）。
- 判据：requirements/requirement-20260922-boundary.md（纳入范围内零缺陷 + 排除项全部登记）；
  reviews/round13-review-brief.md 硬要求 1~7。
- 纪律声明：未修改被审代码、未 git commit（收尾 `git status --porcelain` 仅新增本报告目录与 _r2tmp/r13q 探针沙箱）。

## 裁决：**CHANGES REQUIRED** —— 纳入范围 finding 2 条（Q13-A/B，均实测复现+端活证，
与 F-12-3 同根同族=改动B 组合面修不完备，非本轮引入、三代既有）；
制品名实 NOTES 3 条（Q13-C/D/E）。

---

## 0. 方法与基线核证
[DONE]

| 声称 | 独立核验 | 结果 |
|---|---|---|
| 工作树代码 = 10a2094 态 | 工作树 handler.py sha256 前16 = `cf61f3291970a021`；git blob = `2100d5cc…`，CRLF→LF 归一化后逐字节等于工作树（71412/72706 字节差=行尾 1294 行）——Brief 的 blob/工作树双坐标并存系行尾差，内容一致 | ✅ |
| 部署同代际 | 主部署 + profiles/{architect,developer} 三处 handler.py 均 `cf61f329…0141` | ✅ |
| test 29+4+347 ALL PASS | `python test_handler.py` → ALL PASS (29+4+347)，TC-R13 恰 18 条（01~18） | ✅ |
| pm_verify_013 30/0 | 独立复跑 → 通过 30 失败 0 | ✅ |
| 九 verify 零失败 | r13 41 / r12 53 / r11 43 / r10 46 / r9 46 / r8 30 / r7 30 / r5 28 / r3 25 全部复跑，失败 0 | ✅ |
| pm_verify_012 23 形零回退 | 复跑 exit 0，c1/c2/c5=PASS、d 族全符期望 | ✅ |
| 基线 19 ok+11 FAIL | **跨代重放**：将 pm_verify_013 的加载路径指向 4e254c8 handler（r12 闭环态），复跑 → 通过 19 失败 11，FAIL 集合恰 = X1~4/T1~3/E1~4 | ✅ |
| fix-013.md 基线声称「代码面 8dde55b 态」 | `git diff 4e254c8..7db304b -- handler.py test_handler.py` 为空 → 等价性成立；但 **`8dde55b` 不存在**（`git rev-parse` fatal，实核），实际 sha 为 `8dde55e`——笔误 | ⚠ 见 Q13-C/E |

探针工具勘误（自查）：首轮用 `_judge_terminal` 直连测「gateway restart 红线」得 PASS——
入口错位（红线在 on_pre_tool_call 守卫 D 层，非 terminal 写矩阵）；Z2 形 want=approve 系照抄
规格文字。终版红线改走 `on_pre_tool_call` 正确入口，Z2 单列分叉（见 §4）。

## 1. 代际差分（r12 闭环 → r13 闭环，38 形双向）
[DONE] 探针：`r13q_probe_matrix.py`（old=4e254c8 提取件，new=HEAD 工作树，同进程同环境对照）。

- 翻转 18 形全部落预期面：X1~4/T1~3/E1~4（封堵靶心 11）+ N4（tee 冒号 LiteralPath，
  同 F-12-1 派生面）+ P1/P2/P3（pwsh/sudo×pwsh 载体经 per-cmd 表接管）+ P6（Tee -Append
  插位）+ Q1（`sort "-o<CFG>"` 引号粘连，改动B 自然覆盖 sort 门内）。
- 锁形 20 形零漂移：K 族、N1/N2/N3/N5、P4/P5/P7/P8、Q2/Q3、K13/K14/K18、R2~R4。
- **预期外翻转 1 形 = Z2**：`-Destination ws -Destination CFG` approve→PASS。核验：
  端活证该形=绑定错误零写（§5 活证②），PASS 语义正确、规格「锁实测值不要求改」允许，
  非缺陷；但 fix-013.md §0 表「修后预期 approve」未回填终值——并入 Q13-C。
- 三分句正反两面（句1 判写=X/T/P 族翻转✓；句2 判读否决末位=K2/K3/K4/Z1/Z3 锁✓；
  句3 末位启发=K5/K6/K7/P4/P5✓）。**Z1/Z3 无特判核验**：通读 `_terminal_position_is_write`
  命名支（L747-761），无 Z 组字面量/计数特例；人工推演 + 实测双确认 PASS 系
  「目标标志已绑另一值」句天然导出 ✅（brief §4 特别审项达成）。

## 2. 红线与门禁独立复跑（on_pre_tool_call 正确入口）
[DONE] `r13q_probe_positional.py`：
gateway restart=**block** ✅｜cp 写配置=**approve** ✅｜Copy-Item 源位读=**PASS** ✅｜
rm -r 四守卫层=PASS（approvals 平台层职责，分层不变）✅｜-O URL 红线/等号附录/grep 门外保持。

## 3. CHANGELOG round13 节逐条声称 vs git 史证
[DONE]

- 门禁表 6 行：**全属实**（§0 独立复跑背书，含「19+11 基线」跨代重放）。
- 「修复引入回归第 3 次」链上两前例指涉：**属实**——
  ①r10→r11：fix-011-input.md L5 原文「round10 修复引入回归」双路同根互证（git 史 94998f5 立项句一致）；
  ②r11→r12：review-011-qual L37 Q-11-1=「round11 新引入纳入范围误拦」、fix-012-input.md L11
  「五词表把源参当目标绑定词」（c1/c2/c5=approve 实配）——两前例可稽，本批 r12→r13 系改动A
  根因陈述（review-012-sec「本轮改动引入回退」）成立。
- 但同仓库两枚口径并存无调和：review-012-sec 裁决句称「『每轮修复引入新回归』规律**第 5 次**应验」，
  CHANGELOG 称「修复引入回归**第 3 次**」。两者分母不同（全部修复引入回归 vs 词表类三次同构）但
  文内均未注明口径；且按 CHANGELOG 自定义（词表收窄/放宽压平语义），r9 S-2「出现即写」扩词
  引入 F-9-1 源位误拦为候选前例，是否计入应显式判定一句——见 Q13-D。
- curl `=` 形附录句：与 8dde55e 提交（实测 `=_dst2.txt` 落盘）及 r12-sec 附录 1 活证③一致 ✅。
- Z 组甄别句：与 a5ee7de 规格补丁一致 ✅。

## 4. 名实对拍（brief §5 质量路另核）
[DONE]

- **Q13-C（MED，制品名实，按既往失实修正令口径）**：round13-context.md L7 声称
  「fix-013.md（§0/§A/§B/§N/§V 五段全落）」、pipeline-status.md L40-41 声称
  「fix-013.md 五段+CHANGELOG round13 节全在盘，PM 复跑零缺失」——**实测不成立**：
  fix-013.md §A/§B/§N 三节正文均为「（落地后回填）」占位，§V 验收表 6 行全「（待）」，
  与 git 提交件 10a2094:reviews/fix-013.md 与工作树逐字节一致（未回填非在途丢失，是
  施工时即未落）。对照先例：round12 闭环件 fix-012.md 回填完备（含 DONE/实跑 12 处命中）。
  行为面无损（门禁值经本篇独立复跑为真），属「截断第 7 次」事故下制品收尾被遗漏后又被
  上位文档虚报——修正令级。
- **Q13-D（LOW，口径句）**：§3 所述「第 3 次/第 5 次」双口径与 r9→r10 候选前例的计数边界，
  CHANGELOG 需一句注明分母（如「三次同构 = 词表全局化类；全量规律计数另见 review-012 §裁决」）。
- **Q13-E（LOW，注释名实）**：handler.py L281 注释引用已删除符号名 `_GLUED_NAMED_RE`
  （实名为 `_PS_GLUED_NAMED_RES`；L293-294 删除声明与 `hasattr` 实测一致：旧全局两支真删、
  per-cmd 表在用）。行长：handler 最长 113 ≤120 合规；test 唯一超行 L715=125 为 round8
  登记既有（与 CHANGELOG round8 声明逐字吻合）。fix-013.md 头部 `8dde55b` 幽灵 sha 并入本条。
- 注释-代码其余抽查一致：_pair_unquote docstring（token 化/norm 链不经过）与调用位点
  （L727 判定视图、L988 else 支、复制族门）一致；L265-266 ANY 五词「前置在场」句与
  L747 `named = cmd in (…) and ANY.search(seg)` 一致；L986 复制族不启用句与代码一致。

## 5. 端活证（真 pwsh 7.6.2 / curl 8.1.2 / bash，沙箱 _r2tmp/r13q/live，零受保护路径触碰）
[DONE]

1. **X1 组合可运行且真写**：`Copy-Item -Path src.txt -Destination x1order.txt` → 落盘 10 字节 ✅
   （X 族封堵语义正确）。
2. **Z1/Z3 绑定错误零写**：`Copy-Item … -Destination za -Destination zb` →
   "specified more than once"，za/zb 均未生成；`Tee -FilePath ta -LiteralPath tb` →
   "Parameter set cannot be resolved"，ta/tb 均未生成 ✅——Z 组 PASS=语义正确，
   禁特判声称活证复核成立。
3. **Tee -LiteralPath 真写**：`Tee-Object -LiteralPath t1dst.txt` < src → 文件生成 ✅。
4. **curl 引号粘连真写**：`curl "-o" out2.bin file://…`（rc=0，8 字节落盘）；
   E 族封堵语义正确 ✅。
5. **curl 引号 cluster+空格值真写（→Q13-A）**：`curl "-so" out1.bin file://…/in.txt` →
   rc=0、out1.bin 8 字节内容=源文——shell 剥引号后与裸 `-so <v>` 同义，判定端 PASS。
6. **cp 引号粘连 -t cluster 真写（→Q13-B）**：`cp "-tdstq" in2.txt` → rc=0、
   in2.txt 落入 dstq/ 目录——判定端 PASS。
7. 负向活证：`Copy-Item -Path src.txt posTarget.txt`（-Path 源参+末位位置参目标）**可运行
   且真写**（posTarget.txt 生成，rc=0）——为 Q13-A2 旁路族提供可运行性背书。

## 6. 纳入范围 finding（2 条，全实测+活证；改动B 组合面修不完备，同 F-12-3 义务面）
[DONE]

### Q13-A（LOW~MED·三代既有·非本轮引入）引号包 cluster 选项词 + 空格分离输出值
- **形**：`curl "-so" <CFG> url` / `curl "-sSo" <CFG>` / `wget "-qO" <CFG>` /
  `sort "-ro" <CFG> d.txt`（对照裸形 `-sSo`/`-ro` 均 block——只差一层整词引号）。
- **复现**（当前 handler）：`r13q_probe_q2.py` → 四形全 PASS；端活证 §5-5：curl rc=0
  实写 out1.bin。判据：纳入3（整词引号选项，`cp '-t' <dir>` 同级）×纳入1（curl -o）
  组合面，与 F-12-3 备案理由（「纳入3×纳入4 组合义务面」）同构——改动B 只修了值段粘连
  进引号的半边（`"-o<CFG>"`），选项词带 cluster 前缀+值在下一 token 的半边未覆盖：
  `_OUTPUT_QUOTED_RE` 内容段限「仅选项词」（PM 修正约束不回退，正确），`_pair_unquote`
  仅入 `_GLUED_O_RE` 匹配输入。r12 对照同 PASS（非回归，系修不完备残留——恰是 r13 教训
  「组合面验收须含活证」的复现）。
- **修法方向**（≤3 行，勿再压全局）：`_OUTPUT_QUOTED_RE` 内容段并「cluster 前缀+尾 o」
  支（`[\x27"][a-zA-Z]*[oO][\x27"]\s*$` 形，比照 _OUTPUT_FLAG_RE dash 专属 cluster 支
  同款字符类，双 dash/`-O` 大写红线不扩），值仍走既有后随 token 判定；必测负例：
  `curl "-oL" url`、`grep "-so" x`（门外）、`"-H"` 任意引号词——`r13q_probe_q2.py`
  即回归面。

### Q13-B（LOW·三代既有）引号包粘连 `-t<dir>` cluster（复制族，反缴械向）
- **形**：`cp "-tdst" src`、`copy "-t<home内目录>" x` 等。
- **复现**：`r13q_probe_q2.py` Q4 → PASS；端活证 §5-6：cp rc=0 文件落目标目录。
  目标为守卫目录/home 时=纳入7 写目标面（同 F-12-3 的守卫源码同族风险）。
  根因同 Q13-A 镜像面：`_GLUED_T_RE` `^-` 不吃引号起始 token，`_COPY_T_QUOTED_RE`
  内容段限「仅 -t/--target-directory」整词；L986 注释「复制族 cmd 不启用（剥引号）」
  的理由仅针对 -o，未覆盖 -t 族自身缺口。属排除1 分界另一侧（引号未劈 token=整词），
  纳入范围。
- **修法方向**（≤2 行）：收集位点对复制族 cmd 亦以 `_pair_unquote(raw)` 入
  `_GLUED_T_RE.match`（仅匹配视图，norm 链不动——F-7-2 禁令不回潮；与改动B 同法同纪律）。
  或裁决登记为本族终面边界——但需修订 L986 注释理由并补 TC 锁向，不得静默。

- 「三代既有」代际实测背书：`curl "-so"`/`cp "-tdst"`/`sort "-ro"` 三形在
  94998f5(r11)/4e254c8(r12)/HEAD(r13) 三代表层均 PASS——非本轮引入，系组合面残留。

> 两 finding 合计 ≤5 行量级、零新解析层、无特判新增——灰区判据（5 行内可修不引新层）= 做。
> 若 PM 裁决不立项，须按 boundary 判级流程在 CHANGELOG「接受边界」节登记+TC 锁向，不可裸奔。

## 7. 其余特别审项结论（brief §4）
[DONE]
- `_pair_unquote` 非粘连整词误拦面：9 形探针零新误拦（引号路径位 URL 参/`"-oL"`/引号
  `"-H"`、`-Destination:="CFG"` 非可运行形 PASS 保持）——新旧对照同值（§1 差分含）。
- tee `-FilePath "CFG"` 经 gn 支：N2/N3 approve 正确（引号值两段 gn/own 双路达判）。
- pwsh 载体递归 × per-cmd 表 × -Command 载荷：P1~P3 approve、K12 锁、`-Path` 源参形
  （K4）经载体不翻转——载荷 cmd 词解析不受影响。
- 缩写别名/`-Recurse` 等 r12 附录族零变化抽查通过（X5 邻界不扩）。

## 8. 裁决明细
[DONE]
**CHANGES REQUIRED** —— 纳入范围 2 条（**Q13-A** curl/wget/sort 引号 cluster 选项词+
空格值真写旁路，实测+curl 活证；**Q13-B** cp 引号粘连 -t cluster 真写旁路，实测+cp
活证；均系 F-12-3 同族组合面修不完备、非本轮回归、灰区判据=做）；NOTES 3 条
（**Q13-C** fix-013.md §A/§B/§N/§V 未回填而上位两文档虚报「五段全落」——修正令级+
幽灵 sha 8dde55b；**Q13-D** 「第3次/第5次」双口径一句调和；**Q13-E** L281 注释引用
已删符号名）。代码行为面：基线四坐标、门禁 12 项、九 verify、pm012/013、跨代 19/11
重放、红线四形、三分句两面、Z 组无特判、代际差分 18/38 全落预期——除 Q13-A/B 外全绿。

（探针存档：r13q_probe_matrix.py / r13q_probe_q2.py / r13q_probe_positional.py /
r13q_pm013_on_old.py / r13q_ab.py；旧代 handler 提取件与活证沙箱在 _r2tmp/r13q/）
