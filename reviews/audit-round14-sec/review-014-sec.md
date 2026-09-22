# write-guard round14 安全路独立终审报告（review-014-sec）— 终版

- 审计角色：安全路独立终审（sa-0）
- 基线核验：git HEAD=`7b5bddb`（代码 8611f3c 态），工作树/主部署/双 profile 镜像
  handler.py sha256=`0a93ac9caf8ee25e...` **四处一致**；handler.py=1318 行全文通读。
  - 观察项（移交质量路对拍）：round14-context/任务书所写 `src/write_guard/handler.py`、
    `plugins/write-guard/SKILL.md`（1709 行）与实况（repo 根 `handler.py`、无 SKILL.md、
    1318 行）不符——sha/行数以实测为准，声明侧口径失实，非代码缺陷。
- 裁决：**CHANGES REQUIRED**（1 finding：MED 误拦面坐实，1 字符修复已预览零回退）
- 计数：HIGH 0 / MED 1 / LOW 0 / 登记项 3（排除族+观察）

## 1. 门禁复跑（全部独立实测）
- pm_verify_014 27/0、_verify_r14 43/0、pm_verify_013 30/0（不回潮）、
  test_handler **ALL PASS（29+4+363）**、九 verify 41/53/43/46/46/30/30/28/25 全 0、
  pm_verify_012 目检无偏（a1~4/b1~2/d 系列现值正确）。

## 2. 全族粘连入口逐分支翻转表（独立构造 37 形，假 home 沙箱，_r2tmp/r14sec*）
- -t 族：A1~A4/A7~A9 全 hit（含 `-rt` cluster、`--target-directory=` 整包、install）。
- of= 族：B1~B3/B5 全 hit（`"OF="` 大写同拦=多防方向）。
- -o 粘连族：C1~C4、D1~D4、E1~E5 全 hit；**引号整包非保护零误拦 F1~F4 全 PASS**。
- 旁路探针（FAIL→端活证后改判正确）：
  - A5 `cp x "-t<DIR> "` / C5 `curl "-o<CFG> "` 引号内尾空格 → PASS。
    **端活证**：`cp "-t<dir> "` rc=1 No such file or directory；`curl "-o<file> "` rc=37。
    带尾空格目标≠受保护目标，命令端整体报错零执行——与 Z 组双绑必败同构，
    **PASS=语义正确禁特判，登记不修**（登记项 R-1）。
  - B4 `dd " of=x"` 前导空格 → PASS；端活证 rc=1 unrecognized operand 零写，同登记。

## 3. FINDING S14-1（MED，改动B cluster 支误命中面坐实）
**现象**：`_OUTPUT_QUOTED_RE` cluster 支字符类为 `[-]?`（dash 可省），引号内**纯字母
o/O 结尾单词**即可命中（无 dash 亦行）。当前 handler 实测复现：
```
curl "Cairo" <CFG>        -> block    （裸形 curl Cairo <CFG> = PASS）
sort "logo"  <CFG> d.txt  -> block    （裸形 = PASS；真语义=读文件 logo）
curl "o"/"O" <CFG>        -> block    （裸 O/o = PASS；"O" 为任务书点名负例）
```
唯一切换量=引号，方向为**过拦**（本轮修复目标引号语义对齐的反方向残留）。
curl/wget/sort 段内任何引号包 o 尾字母词+受保护路径（作 URL/文件名/字面参数）即 block。
规格 fix-014-input.md 改动B 原文 `["'][-]?[oO]...` 即含此缺陷——"单 dash 专属"仅指
双 dash 不扩，未禁 dash 省略；裸形 `_-OUTPUT_FLAG_RE_` 有 `(?:^|(?<=\s))[-/]o` 独立
锚，引号支无 dash 即无选项语义。
**端活证**：`sort "logo" <CFG>` 纯读实锤（rc=1 文件不存在，无任何写语义）；
红线「引号整包非保护=PASS 零误拦」被此类形态打破（受保护路径在同段时）。
**修法（1 字符，已全量预览零回退）**：`[-]?` → `[-]`（强制单 dash 前缀）。
- 内存猴补丁+副本补丁双验：pm_verify_014 27 形 **0 翻转**（T11~T14 hit 锁、
  T18 `-oL`/E6/E8 零误拦锁全保持）、test_handler 29+4+363 **ALL PASS**、
  FP1/FP5/FP7/FP8 block→PASS 全消、门外 grep 面不动（gn 支走 raw 不经 _raw_ou）。
- 同建议：TC-R14 补锁 `curl "Cairo" <CFG>`/`sort "logo" <CFG>` 负例两形。

## 4. 改动B 其余面 + _pair_unquote 位点串用核（无缺陷）
- `[-]?` 支外：`"-o"`/`"-O"`/`"-so"`/`"-qO"`/`"-ro"`/双引号单引号交替全对；
  `"-oL"`/`"-H"`/`"--o"`/`"--output"` 既有锁无回退；URL `/logo` 含符号不进字符类
  （FP3/FP4/FP13/FP14 PASS）。
- `_pair_unquote` 调用位点 grep 清点 6 处（L721/798/801/990/1012/1013）：全部仅
  判定视图/前缀提取视图；token 化与 norm 链不经过（F-7-2 不回潮）；L1012 复制族
  门 `_ou = raw if cmdw in _COPY_CMDS` 分流正确，无判定/norm 串用。
- `--output=` 长形 block 面：wget `--output-document=` 真语义同拦方向正确
  （curl 端死选项=无害多防，附录句保持）。

## 5. 红线复验（入口层 on_pre_tool_call）
gateway restart=block ✓；cp 源位读=PASS ✓；cp 目标写=approve ✓；mv/ren/rename=PASS
（OOS-09 声明边界）✓；rm -r=插件 PASS（平台 approvals 分层，r9 登记口径）✓；
write_file/execute_code 写配置=block ✓；引号整包非保护=PASS ✓。
**唯 S14-1 一类（段内含受保护 token 的引号字母词）破零误拦红线**——即本 finding。

## 6. 登记项（不立项）
- R-1 引号内尾/前空格粘连形（cp "-t DIR " / dd " of="）：端不存在（活证 rc=1/37），
  语义正确 PASS。
- R-2 观察：round14 上位文档 handler 路径/行数/SKILL.md 声明与实况不符（移交质量路）。
- R-3 既有声明边界（劈 token/robocopy 零兜底/os.spawn 族）无回潮，不重复登记。

## 7. 裁决
**CHANGES REQUIRED**：仅 S14-1（MED，1 字符 + 2 锁形），修复预览已双路径全量回归
零翻转；改动A 本体（四支+提取位点）与 NOTES 批独立活证**零旁路、零回退**，
粘连入口引号整包族封堵目标达成。修复合入后安全路可复审放行。

（全文实测背书：_r2tmp/r14sec_flip*.py、r14sec_live.py、r14sec_fix/handler.py 补丁副本；
被审代码零改动、未 git commit。）
