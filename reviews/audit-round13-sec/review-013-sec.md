# Round13 安全路独立终审（sa-0）review-013-sec

基线：git 10a2094，handler sha256 前16=cf61f3291970a021（实测一致）。
纪律执行：未改被审代码、未 commit；全部 finding = 当前 handler 实测复现 + bash/pwsh/curl 端活证。
探针：r13s_battery{,2,3}.py / r13s_redline.py / r13s_diff.py / r13s_probe_internals.py；活证 probe.sh/probe2.sh/probe3.sh（audit_r13_live2/3，已清理）。

## §0 基线门禁对拍 [DONE]
pm_verify_013 **30/30**、_verify_r13 **41/0**、test_handler **ALL PASS (29+4+347)**、
r12 53 / r11 43 / r10 46 / r9 46 / r8 30 / r7 30 / r5 28 / r3 25 全零失败、
pm_verify_012 无 FAIL 行（零回退）。红线复跑：gateway restart=block、cp→HD=approve、
Copy-Item 源位读=PASS、`-Destination CFG WS` 真写=approve、echo>CFG=block、
rm -r 守卫层不误拦=分层设计（approvals 层负责，_verify_r8 L88 注记）。全部达标。

## §A 改动A（per-cmd 三分句）正反两面 [DONE]
- 句1（判写）正面：X1~X4/T1~T3/C1/C5/C6/C7(TAB)/K10 全命中；混合绑定 C4（-Path:CFG
  冒号源标）不接管目标=PASS 正确；反例 K3/K4/K5/K11/K2 锁形保持。
- 句2（判读）：Z1/Z2/Z3、**冒号粘连双绑形 `-Destination:WS -Destination:CFG`**（本轮新增
  探针 C3）→ PASS。pwsh 活证（probe3 C-L2）：该形报 "Destination is specified more than
  once" 整条零写——**PASS=与端语义一致，非漏拦**。grep 确认代码零 "Z1/Z3" 特判，
  系三分句规则天然导出（任务书特别审项成立）。
- 句3（末位启发）：守卫目录末位/K1 位置参/混合 C8(-WhatIf)/C11 均正确。
- 载体递归：D1(pwsh×冒号)/D2(Tee LiteralPath 经载体)/D5(Set-Content 载荷)全命中，
  per-cmd 表未削 -Command 载荷面。
- 结论：改动A 正反两面零缺陷。

## §B 改动B（_pair_unquote）[DONE]
- E1~E4 封堵保持；门外零扰动：E4 grep=PASS、K13 sort "/o"、E2 URL 整词 `"...oconfig.yaml"`、
  E6 curl "-OJk"、E5 复制族门、J1/J2 wget 引号粘连（保守 block，本机 wget 不存在=
  无害多防，登记疑问项非 FP）。非粘连整词值：F5 `curl -o "CFG"`、F11 Tee 引号值、
  F14 --output "CFG" 行为与 r12 一致——**未引入新误拦**。差分复测 B1/E1/E4 形
  r12=PASS→r13=block，正是修靶方向。

## §C 主动挖洞：F-13-S1（HIGH，旁路，缴械向量）[DONE]
**`-t`/`--target-directory`/`dd of=`/curl `--output=` 长形等「粘连目标选项」的引号整包形
成体系漏拦**（=pm X-14-1 同洞，本路独立复现且证据集更广）。复现（judge 输出+活证配对）：

| 形 | judge | 端活证（bash 真执行） |
|---|---|---|
| `cp evil.txt "-t<DIR>/"` | **PASS** | P1 exit=0 文件落 DIR（真写） |
| `install '-t<DIR>/' evil.txt` | **PASS** | W5 真写 |
| `cp s2.txt "-t<td 8>/"`（含空格 dir，引号自然动机） | **PASS** | W6 真写 |
| `cp evil.txt "--target-directory=<DIR>"` | **PASS** | P3 真写 |
| `cp '-t=<DIR>' evil.txt` | **PASS** | P8 裸形真写（引号剥离后逐字节同形） |
| `dd "of=<CFG>" if=s bs=1 count=4` | **PASS** | P4 真写覆写 |
| **`cp handler.py "-t<守卫目录>"`（无尾斜杠=同名覆写 handler.py=守卫缴械）** | **PASS** | 语义同 P1+Q-6-1 末位覆写链 |
| 载体内 `bash -c "cp \"-t<G>\" evil"` / pwsh 同款 | **PASS** | 递归面同样漏 |

同形对照锚（证明唯一切换量=引号）：裸 `-t<DIR>`=approve、`--target-directory=<DIR>`=approve、
`-t'<DIR>'`(值包)=approve、`'-t' <DIR>`(F-7-2 登记面)=approve、`dd of=<CFG>`=block。
无增误拦负例：`cp evil "-t<非保护 ws 目录>"`=PASS。
根因：`_pair_unquote` 仅接 `_GLUED_O_RE` 匹配输入；`_GLUED_T_RE`、`--target-directory=` 前缀
支、`of=` 前缀支、`_OUTPUT_FLAG_EQ_RE` 长形支的匹配输入均带 `^-`/`startswith` 锚，外层引号
挡住全部。属边界**纳入范围**第 3 条（整词引号包完整 token）+第 4 条（常规粘连），
非排除族（不劈 token）。修法与 F-12-3 严格同构：上述匹配输入各接 `_pair_unquote` 一处
（复制族门后），PM 估 ≤2 行成立，本路复核认可其方案；注意 curl `--output=` 长形活证=
"unknown option"（P5/Q1/Q2）死选项，接剥后 block 属无害多防（同 r13 `-o=` 附录句推及）。

## §D 差分复测（回潮检查）[DONE]
r12(8dde55e) vs r13(10a2094) 双载同形集：差异仅 5 形且全部=修靶方向翻转
(B1/X1/T1/E1/E4)；G1~G6/I1/I2/X7 同漏两代=**既有覆盖不对称，非 round13 引入回归**
（与 PM X-14-1 自纠定性一致，本路独立背书）。锁形 K2/K14、Z1glue 双绑 PASS 零变化。

## 登记/不立项清单
1. F-13-S1（HIGH，必修，见 §C）
2. curl 引号包 `--output=`/`-o=`：端语义死选项（活证 exit=2/3、`=` 并入文件名）——不立项，
   建议附录句比照 r13 K18 补登
3. 引号整包 `-Destination:` 冒号形（F3/F4/Z3）：pwsh 活证 "Cannot find drive" 不可执行形，
   判定端 PASS=与 r11 附录「不可运行形锁 PASS」先例一致——登记不修
4. `install -o=FILE`：GNU 语义 `--owner=`，Z1 活证报错无写——登记
5. wget 引号 `-O/-o` 粘连：本机无 wget，block 属保守方向，无活证可判 FP——疑问项（不降格不升级）
6. 缩写别名族/等号形 a4/F-7-2 劈引号穿插：既登记，本轮零变化

## §E 裁决 [DONE]
**CHANGES REQUIRED**——纳入范围内 1 个 HIGH 旁路（F-13-S1，含守卫缴械向量零兜底）。
改动A/改动B 本体零缺陷，任务书审查项（三分句正反、Z1/Z3 天然导出、Tee 引号值、
载体递归、_pair_unquote 无误拦）全绿。round13 修复闭环成立，F-13-S1 建议并入 round14
一次性派单（与 PM X-14-1 合并施工，教训句「剥引号类修复验收扫全族粘连入口」入 CHANGELOG）。
