# review-008-qual：write-guard round8 终审（质量路，只读）

- 评审对象：workspace/write-guard @ git a0dab67（round8）+ 部署一致性 + 镜像通道
- 最高准绳：requirements/requirement-20260922-boundary.md（2026-09-22 范围决策）
- 判据：纳入范围内零缺陷 + 排除项全部登记在案；排除范围形态不立项（附录罗列）
- 纪律：全程只读（探针脚本落本目录；未动 handler/test/deploy/部署目录/git）
- 探针：q8_nominal_probe.py（登记句逐条对读）、q8_probe2.py（新形+当前码）、
  q8_probe3_baseline.py（pre-r8 基线行为锚定，直载 reviews/fix008-scratch/
  handler.pre-r8.py，其行尾归一 sha 实测 == git 90de321:handler.py）、q8_ast_scan.py

## 裁决：**PASS_WITH_NOTES**

纳入范围内未发现新缺陷（质量路抽查口径）；验收基线全数复跑达标；登记句行为口径
逐条实测为真。NOTES 五条均为文档级微疵/登记锚缺失（N1~N5），无代码回改必要。

---

## 1) 实跑验收（无回潮）

| 套件 | 声称 | 实测 | 判定 |
|---|---|---|---|
| test_handler.py | 29+4+250 ALL PASS | `ALL PASS (29 scan + 4 hook + 250 new)`，TC-R8-01~17 全绿，TC-R7 14 条保持绿 | ✅ |
| _verify_r8.py | 30/0 | 通过 30 失败 0（场景实数=30，与"30 场景"名实相符） | ✅ |
| _verify_r7.py | 30/0 | 通过 30 失败 0 | ✅ |
| _verify_r5.py | 28/0 | 通过 28 失败 0 | ✅ |
| _verify_r3.py | 25/0 | 通过 25 失败 0 | ✅ |

fix-008.md 数字口径抽查：§0"handler 现 1129 行"= git 90de321 实测 1129 ✅；
§1"git diff 共 +47/-3"= numstat 47/3 ✅；§5/§6 登记与验收记录与实跑一致 ✅。

## 2) 名实一致性：CHANGELOG 每条登记句 vs 实测行为

### 2.1 round8 新登记「接受边界」族逐条对读

| 登记句（L30-33） | 实测（q8_nominal_probe / q8_probe2 / _verify_r8） | 判定 |
|---|---|---|
| 劈 token 穿插族 cp -'t'DIR PASS | `cp -'t'GUARD`/`cp -"t"GUARD`/`install -'t'HOME`/`install -"t"HOME` 全 PASS；对照整词 `cp '-t'GUARD` approve（区分度与 boundary§排除1"引号是否劈开一个 token"一致） | ✅真（TC-08/r8 锚定） |
| 双引号内 bs+LF PASS | `echo "a\LF+GUARD"` PASS；TC-04+r8 锚定 | ✅真 |
| 反引号混排 PASS | r8 实测 PASS；TC-…（r8 54 行锚定） | ✅真 |
| 4bs+LF PASS / 3bs+LF approve | 实测 PASS/approve；且扩展 5bs=粘连 approve、6bs=分段 PASS——"反斜杠逐对消耗自然满足奇偶语义"对 POSIX 真值（fix-008-input §1b）方向成立 | ✅真（TC-06/07 锚定） |
| **半混劈 token tdir= 变体 PASS** | 候选形实测均 PASS（行为方向真），**但 _verify_r8/TC-R8 均无该形锁向场景** | ⚠ N1 |
| F-7-3 保守弹卡 FP 接受 | 实测 `cp '-t' CFG out/` → approve（保守方向真）；**无 TC 锁**（弹卡为默认行为，锁缺失风险低） | ⚠ N1 |
| 跨家 tilde 维持 F-Q5 登记 | round6 节 F-Q5 在案，口径连续 | ✅真 |

总括句"均 TC 锁现状方向"对第 5、6 项不成立（缺锚），行为本身无误 → 归 N1。

### 2.2 round8 修复项登记句

- F-7-1"实测真续行 LF/CRLF approve、2bs 分段旁路封、gateway 两形红线 block 保持"
  ——当前码逐项实测全真（TC-01/02/03/14/15、r8 37/38/43/85/87）✅。
  基线对照（q8_probe3）：真续行 LF/CRLF 基线=approve（盲替换"恰好"封堵，与
  fix-008 §0"恰好粘连成一行"口径一致）；2bs 分段基线=PASS（旁路，修后 approve=
  真修复）；gateway CRLF 基线=PASS（旁路，修后 block=真修复）。
- F-7-2"两引号形 approve、非 home 负例放行"——实测 sq/dq tdir=GUARD=approve、
  workspace 负例 PASS、裸形对照不回潮、`'-t'=GUARD` 随同款链 approve（§0 行23
  声称逐字为真）✅。elif 分支判定确由 `_COPY_T_QUOTED_RE.search(seg[:m.start()])`
  before 门把关，未引入通用引号剥离（红线保持）✅。
- 数量词微疵见 N2。

### 2.3 round7 修正括注（L53-55）对读

"盲 replace 不感知引号态与反斜杠成对，2bs+LF 真分段形被误并（旁路）与 gateway
CRLF 续行形实际未封"——两项均实测为真（p2/p3 基线 PASS）；括注未过度声称"真续行
曾被旁路"（基线实为 approve，与括注沉默相容）✅ 修正口径如实。

### 2.4 历史文档矛盾备案（非本轮登记句，不计 finding）

fix-008-input §1.1 称"真续行修前=PASS（合法续行攻击面从未封住）"——基线实测
approve，该 PM 复验声称失实；已被 fix-008 §0"恰好粘连成一行"口径覆盖修正
（历史输入文档按时点快照原则不回改，与 CHANGELOG 末节惯例一致）。

## 3) 三份文档口径互洽

- boundary（纳入1-7/排除1-4）↔ CHANGELOG round8 概述段：纳入列举、排除列举逐族
  对应无分叉；"整词包裹纳入、劈 token 排除"区分标准与 handler 行为、TC-12/13
  锁向三方一致 ✅。
- fix-008 §0 处置列全部引用 boundary/OOB 更新口径，逐行与实测一致（含双引号内
  "不处理=登记"对 fix-008-input"双引号内同删除"的改判——改判有据：boundary
  §排除2 生效在后）✅。
- decision 原话与 boundary 引用逐字一致；两文档互指（decision→boundary）✅。
- 微疵：boundary §排除3"（…）均已有登记"对 **heredoc 内嵌脚本深递归**无 CHANGELOG
  明文条目（NL 分段修复实际已覆盖该形方向）→ N5。
- 灰区裁决链条一致：boundary"F-7-2 若一行为及则顺手修、禁引号剥离通用机制"↔
  fix-008 §2"两行可修=做、判定复用 -t 矩阵门"↔ CHANGELOG"灰区两行判定=做"✅。

## 4) AST/腐化常规扫描（q8_ast_scan.py）

- ast.parse 通过；handler.py 无 >120 长行（最长 113，L525/535=113/110 合规段）✅
- 顶层名零未引用（死常量=0）✅
- 续行族盲 replace 残留=0（剩余 .replace 均为转义/斜杠归一/三引号折叠等既有合法
  用途，L372/406/411/424/939/966）✅；_join_line_continuations 定义 1 + 接入 2
  （terminal 入口 L799、守卫 D L1120）与设计一致 ✅
- Q-6-2 收敛保持：守卫目录字面量单源 _GUARD_DIR_SEG_RE（L612 定义、L616 docstring
  提及）✅；_is_guard_dir_target 无死支回潮迹象 ✅
- 登记边界行为哨兵：tar -C、robocopy 零兜底维持 PASS（与登记一致）✅
- 环境残留：worktree 仅 `M reviews/pipeline-status.md`（PM 状态更新未提交）+
  本评审目录 untracked；`_verify_r*.py`/`fix008-scratch/` 均在 .gitignore 口径内
  （scratch 的 apply/probe 件属"任务型一次性脚本"清理位，收尾步骤 3 处理）✅

## 5) 部署一致 + 镜像（只读 sha 对比，未改）

| 文件 | 主部署 | 镜像 architect | 镜像 developer | 三者互比 |
|---|---|---|---|---|
| handler.py | c1b3ddb0…(sha256 raw，全 CRLF) | c1b3ddb0… | c1b3ddb0… | **一致 ✅** |
| plugin.yaml | 59bc50cc… | 59bc50cc… | 59bc50cc… | 一致 ✅ |
| __init__.py | a0e39b04… | a0e39b04… | a0e39b04… | 一致 ✅ |

- 部署 handler 行尾归一 sha=fd3f1423 == git 90de321 内容（round7 代际）✅；
  git HEAD a0dab67=fb19f8fc 未部署——按门禁"复审 PASS 后才允许部署"，**预期状态，
  不列 finding**（OOB 判定补充执行）。
- pipeline-status.md 声明"当前部署代际=round7"与现场**代际相符**；但括注
  "handler sha 前缀 b8f1217a"与现场任何变体（raw/归一/换行互换/sha1）均不符
  （现场 16 位口径=c1b3ddb07c553805）→ N4（文档句失实，代际声明本身为真）。

## 6) NOTES（均不构成 CHANGES REQUIRED）

| # | 级别 | 内容 | 建议（PM 顺手处置，不阻断） |
|---|---|---|---|
| N1 | 文档疵/锚缺失 | CHANGELOG 接受边界"半混劈 token tdir= 变体 PASS"与"F-7-3 保守弹卡"两族行为实测为真但无 TC/_verify 锁向场景，总括句"均 TC 锁现状方向"不成立 | 补 2 条锁向场景或在登记句去掉"均"字 |
| N2 | 措辞疵 | round8 F-7-1 句"两处盲 replace（terminal 入口 + gateway 守卫，第三处同源）"数量词自相矛盾（实为 2 调用点、3 替换操作，terminal 侧一行链式双 replace；fix-008 §1"三处"同样歧义） | 统一为"两处调用点（其中一行链式替换 LF/CRLF 两形）" |
| N3 | 承诺缺失 | fix-008-input F-7-4①要求在 CHANGELOG 明文写行长阈值=120，CHANGELOG 无该句（handler 现无 >120 行、test_handler L715=125 为 round8 前既有，阈值句若落地需注明仅约束 handler） | CHANGELOG round8 节补一句 |
| N4 | 文档疵 | pipeline-status.md（未提交改动）"handler sha 前缀 b8f1217a"失实，现场=c1b3ddb0（代际声明 round7 为真） | 改现场值 |
| N5 | 登记过称 | boundary §排除3"（均已有登记）"对 heredoc 深递归无 CHANGELOG 明文条目（NL 分段行为已实际覆盖） | 补一句或删"均" |

## 7) 附录（排除范围形态观察记录，不立项）

`cp -'t'-GUARD` 逐字符拆引号、`-"target-directory"` 半混 tdir=、2/4/6bs+LF 分段族、
双引号内续行、反引号混排——实测均 PASS，均属 boundary 排除 1/2 族，登记口径
与行为闭合。误拦侧：`cp "-t" GUARD x`（整词空格式）approve 为纳入范围 3 应然方向，
非误拦。

—— 质量路终审完毕（2026-09-22）。裁决：**PASS_WITH_NOTES**（NOTES 5 条，全为
文档级；纳入范围内零缺陷，排除项登记除 N1/N5 措辞外全部在案，验收基线零回潮）。
