# Round14 质量路（sa-1）独立终审报告 — fix-014 / 制品·注释·CHANGELOG·git 史证对拍

- 基线：git HEAD=7b5bddb，代码态=8611f3c（工作树 handler.py sha256 前16=`0a93ac9caf8ee25e`，
  与 brief/context 宣称一致；blob 侧 CRLF 归一后=`dd1c0cd92abc3a31` 工作树=提交态逐字节一致实测）。
- 部署面：主部署 + profiles/{architect,developer} 三镜像 handler=`0a93ac…` 一致；
  `__init__.py`/`plugin.yaml` 四目标同哈希（a0e39b…/59bc50…）——deploy 完整性成立。
- 纪律：未修改被审代码、未 git commit。临时脚本仅落 _r2tmp/（gitignore 登记区）。

## 裁决：**PASS_WITH_NOTES**

阻断项 0；NOTES 级 finding 2（Q1/Q2，均为文档-实现名实面，非旁路非红线破口）；
如实登记项 3（Q3~Q5）。代码面改动A/B 本体、门禁数组、红线、制品纪律、git 史证**全对拍属实**。

---

## C1 基线与 git 史证对拍 [DONE]

- `git diff 8611f3c..HEAD` 仅新增 round14-context.md / round14-review-brief.md 两文档，
  代码零漂移 ✅；context 宣称「代码 8611f3c 态」成立。
- 8611f3c 提交面（stat）：handler.py 64 行 / test +59（TC-R14 16 条实点计=16）/ CHANGELOG +69 /
  fix-013 回填 / fix-014.md 新建 162 行 / pm_verify_014 1 行（末行打印三元式笔误修正，
  diff 实核零断言影响）——提交说明逐句与 diff 面一致 ✅。
- 三代既有宣称：T2/T4 在 94998f5/4e254c8/10a2094 三 handler 快照实跑全 PASS（旁路系既有）✅。
- 幽灵 sha：`8dde55b` rev-parse 不存在、`8dde55e` 存在——fix-013.md 头部修正句属实 ✅。
- 立项记录「13 靶心 FAIL/16 ok」：旧 handler 代跑（_r2tmp/pm014_oldh.py，本轮独立重跑）
  FAIL 标签 =T1~T7/T11~T15/T17 **13 条全对**；「16 ok」含表头两行旧口径（14+2），
  fix-014.md §0 已如实注 ✅。input §完成定义「29 形」与表实 27 行的出入同属该旧口径（Q4 登记）。

## C2 改动A/B 代码直读 + 邻域 [DONE]

- 改动A 四支接点（_GLUED_T_RE / `--target-directory=` / `of=` / _OUTPUT_FLAG_EQ_RE 长形）
  判定视图+收集视图**成对施工**实核，全部命令门后；token 化/norm 链不经 `_pair_unquote`
  （F-7-2 不回潮）实读成立 ✅。
- `_pair_unquote` 调用位点 grep 清点：7 处（L721/L732/L798/L801 判定视图；L990 提取视图
  含 5 前缀匹配；L1012 _ou 复制族门控；L1013 T 族收集）——**判定视图/norm 视图零串用**：
  is_dir_target（L1025）仍走 raw 剥尾引号，norm 输入=剥壳提取值，逐字节同构 ✅（任务书§2 邻域项）。
- 改动B 正则 `[\"'](?:-[oO]|--output(?:-document)?|[-]?[a-zA-Z]*[oO])[\"']` 与规格 §B 形
  逐字符一致；三门命令门后（curl/wget/sort）✅。

## C3 六类粘连入口逐分支翻转+端活证（教训固化句对复审自身的约束）[DONE]

| 类 | 形 | 判定端 | 端活证（本轮沙箱真执行） | 结论 |
|---|---|---|---|---|
| -t 族 | `cp '-t<PDIR>'` | approve | bash：`cp ok1.bin "-t./tdir"` → tdir/ok1.bin **真落盘** | 封堵=语义 ✅ |
| of= | `dd "of=<CFG>"` | block | bash：`dd "of=qo.bin"` → **真写 size=4**（与裸同义）| 封堵=语义 ✅ |
| --target-dir= | `cp "--target-directory=<CFG>"` | approve | 同族 r7 裸形已证 | ✅ |
| --output= 长形 | `curl "--output=<CFG>"` | block | curl 8.1.2 实测：**裸与引号均 "option is unknown" rc=2 零写**；`--output-document=<CFG>`（wget 域）与裸形均 block；curl `-o "=clu_out.bin"` 实测落盘 `=clu_out.bin`（=并入文件名语义实证）| 死选项定级方向成立、多防无害；**机理句失实→Q2** |
| 冒号形 | `Copy-Item "-Destination:<CFG>" ws` | PASS | pwsh 实测：**"Cannot find drive" 绑定错误零写、文件不存在**（Tee `-FilePath:` 同）| 不可运行形 PASS=语义正确，禁特判（同 r13 Z 组先例）→Q3 登记 |
| cluster+空格值 | `curl "-so" <CFG>` 等 | block | 立项链（ecca470/04:00 pm013.out）+ 本轮判定端 T11~T14 复跑一致 | ✅ |
| 穿插（排除） | `cp "-t<6>"x/'…` | PASS | TC-R14-16/_verify_r14 双锁复跑 | 排除范围不回潮 ✅ |

非对称形 `dd " of=x"`（引号内前导空格）：判定端 PASS；端活证 dd 拒收 operand
（"unrecognized operand"）零执行——无误拦无旁路，行为干净（Q5 登记）。

## C4 改动B 误命中面探针（任务书§2 点名）[DONE]

- `curl "-oL"`/`curl -O url`/`curl "http://x/o"`/`grep "-so"`/`sort "o" 非保护`：全 PASS 零误拦 ✅。
- **新发现面**：`[-]?` 允许零 dash → `curl "o" <CFG>` 与 `curl "O" <CFG>` 命中 block，
  而裸 `curl o <CFG>` 不命中。端语义：引号裸单字母 o/O = URL/位置参（curl 无选项语义、零写）
  → 该形 block 属潜在误拦（组合本身近无意义，误拦概率极低；安全路独立同面互证）。
  与注释/CHANGELOG「**单 dash 专属**」字面不符 → **Q1（LOW，NOTES）**。

## C5 门禁全量复跑（独立于 PM 记录）[DONE]

test_handler **ALL PASS 29+4+363**（TC-R14 16 条在列，rc=0）；pm_verify_014 **27/0**；
_verify_r14 **43/0**；pm_verify_013 **30/0**；九 verify **41/53/43/46/46/30/30/28/25 全 0**；
pm_verify_012 全 25 行逐值与 round12 期望一致（a1~a3=approve、a4/b4/b5/c1~c3/c5/d5~d10=PASS、
b1~b3/d1~d4=block、c4/c6=approve）零回退——CHANGELOG L67/L72「27/0、23 形」宣称复跑全实 ✅。

## C6 红线六形 [DONE]

R1 cp/R2 mv 源位读=PASS；R3 cp 目标写=approve；R5 gateway restart=block（且拦截消息由
本插件真实弹出）；R6 引号整包非保护=PASS 零误拦；R4 `rm -rf <守卫>`=PASS——**分层正确**：
rm 拦截属平台 approvals 层职责（round8 PM 复核在案 CHANGELOG L300-301，pipeline-status
红线句「rm -r 保持拦截」指全链路），插件层零扰动系设计语义，非缺陷。红线四形另经
_verify_r14 末组复跑一致 ✅。

## C7 CHANGELOG round14 节逐句对拍 [DONE]

立项段/改动A/B 段/附录句/教训固化句/门禁表 7 行/收尾过程段逐句对拍 git 史+复跑，
**除 Q2 机理句外全部属实**。第 7 项审批超时如实登记句：与 round14-context L23-25 及
两次「不重试不绕行」口径一致，且本轮复审端活证在 workspace 沙箱全数成功执行（bash/pwsh/curl
三端），「现场复跑待用户在会话时」义务已由双路复审活证链兜底闭环 ✅。口径调和句（Q13-D）
与 review-012-sec L67「第 5 次」原文引用相符 ✅。注释实名句与 handler L280-282 实态相符 ✅。
瑕疵登记：L57-63「过程」段把第 7 项 bullet 嵌进句中致阅读断裂（内容无损，Q5 附记）。

## C8 制品/fix-013 回填/注释行长 [DONE]

- fix-014.md：§0/§A/§B/§N/§V 五段全落，`[DONE]` 计 8 处=context 宣称「8×[DONE]」✅；
  §0 行为映射表基线/终值双列与复跑一致。
- fix-013.md 回填：§A 行号注「10a2094 提交态，r14 已漂移按符号检索」口径自洽；§B/§N/§V
  内容与 `git diff a927010..8611f3c` 代码史、CHANGELOG round13 节、本轮实测 Z2=PASS
  全一致；「施工未回填声明」保留作事故档案=Q13-C 要求逐字落地 ✅。
- 注释/行长：handler 最长行 118≤120；test_handler 唯一 >120=L715(125) 系 round8 既有登记
  （CHANGELOG L314-315），非本轮引入 ✅。

## Finding 明细

| # | 级别 | 内容 | 建议（不改被审代码，供 PM 收线批裁量） |
|---|---|---|---|
| Q1 | LOW·NOTES | `[-]?[a-zA-Z]*[oO]` 允许零 dash：`curl "o"/"O" <CFG>` block，与注释/CHANGELOG「单 dash 专属」字面不符（实现忠实于规格字形，矛盾在规格注释自反）。端语义零写、误拦组合近无意义。 | 收紧为 `[-]`（1 字符）或注释改「单 dash 或裸字母」并补 `"o"/"O"` 锁形二例（正反各一） |
| Q2 | LOW·NOTES | 死选项句机理失实：CHANGELOG round14/fix-014.md §A-A4 称 curl `--output=` 「=并入输出文件名」——本轮活证裸与引号形均 `option is unknown` **rc=2 零写**；「=并入文件名」实为 cluster 短形 `-sfo=` 机理（r13 8dde55e 档案形，本轮 `=clu_out.bin` 复证实）。死选项定级与「无害多防/禁扩表」结论不变。 | 机理句改「长形=不可运行（unknown option）；短形=并入文件名——两域皆不写真目标」 |
| Q3 | INFO | 冒号类引号整包（全族第六类）pwsh 绑定错误零写=PASS 语义正确（同 Z 组先例），不立项。 | 收线时在排除/不立项档案补一句即可 |
| Q4 | INFO | 「29 形/16 ok」旧口径（含表头）已在 §0 如实注；input §完成定义-1 的 29 同源笔误。 | 留痕已足，无需动 |
| Q5 | INFO | dd 引号内前导空格非对称形=端拒收零执行，行为干净；CHANGELOG L57-63 过程段 bullet 嵌句阅读断裂。 | 排版随收线顺手修 |

**收敛判定**：改动A/B 本体零缺陷（靶心 13 形全翻转+锁形零回退+红线分层正确+端活证
六类逐支闭环），Q1/Q2 属 NOTES 级名实修正，与 round13 质量路 Q13 系列同族同量级。
质量路视角满足「纳入范围零缺陷+排除项全登记」——**PASS_WITH_NOTES**，不阻断
round14 收敛（双路均出裁决后由 PM 收线）。

（本报告为终稿；边测边 [DONE] 回填纪律在 C1~C8 各段落盘执行。）
