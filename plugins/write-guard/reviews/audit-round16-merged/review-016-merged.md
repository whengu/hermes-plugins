# review-016-merged（round16 合并终审：mv 别名视图条件差分 + tilde×载体递归 + 读写位置语义全链 + 名实对拍）

- **裁决：CHANGES REQUIRED**（1 项纳入范围缺陷 F-16-S1，同构修法已 ≤5 行定演；3 条 NOTES 不阻断）
- 基线：git `70948f8`，handler sha256[:16]（CRLF 裸字节口径，N-15-1 口径沿用）=`9295bf170ecb399d`；
  终审独立复跑，2026-09-23。复审在途 PM 补交纯文档决策档案 `6cd8874`（requirements 域，
  被审代码面零差，不构成本报告基线漂移；其内容与本终审核心 finding 直接相关，见 F-16-S1）。
- 探针落 `_r2tmp/r16_audit/`（probe_diff2/probe_focus/probe_fixdemo/v2，git-ignore 内，
  纯判定零落盘，未 commit/deploy）。

## 改动面核对（与规格一一对应，零扩面）

- `git diff 4ddc3ba..70948f8 -- handler.py` = +30/−1；其中纯代码行 19（其余 11 行=5 行段注释
  +2 行消费点行内注释+docstring 行）。fix-016.md 宣称「代码净增 12 行（≤12 达标）」口径为
  「逻辑插入行」（helper 4+消费点 1+1+mv 支 4+词表 1+2 docstring），与 CHANGELOG「+30/−1」
  并读可闭合，但「≤12」与盘上 19 代码行之间无口径句——归 NOTES N-16-3。
- 插入点 4 处与规格 1a~1d 逐一对应（_HERMES_SEG_RE/_protect_view_norm 定义 + _is_protected_
  config 体首 + _is_guard_dir_target 体首 + mv 支 + 词表）；deploy.py/plugin.yaml 未触 ✓。
- 部署一致性：主部署 + architect/developer 镜像四件全 `9295bf170ecb399d` ✓。

## ① mv 别名视图条件差分（焦点项）——达成，不对称性构造正确

- 触发条件三锁全在位：`norm≠视图`（仅别名形到达）∧ `ptoks[-1].start()==m.start()`（仅末位
  目标）∧ 绝对形 `norm==视图` 恒 False（改名红线 L4 零触碰）。实测：`mv x ~/.hermes/cfg` /
  `$HOME 形` / `C:/Users/guwh 旧别名形` → approve；`mv 绝对cfg y`（改名）、`mv ~/.hermes/cfg y`
  （源位读）、`mv x 绝对cfg`（绝对覆写旧有边界）、`mv x ~/.hermes/`（目录目标非文件）→ 全 PASS。
- **有意不对称登记**：同一物理文件，别名形 mv 目标=approve、绝对形 mv 目标=PASS——规格 K3 vs
  L4 明文不对称（别名覆写=内容替换语义论），双路立论一致，接受；建议 NOTES N-16-1 收线时把
  「alias-mv 与 abs-mv 语义分歧」点名为在册设计（防后续轮次当缺陷重挖）。
- `ren` 同入 _MOVE_CMDS 且视图条件命中（ren x ~/.hermes/cfg→approve）——与 mv 同语义，无碍。
- disposition 词表并 _MOVE_CMDS 的影响面核验：绝对形 mv 永不到达该函数（收集/判定双闸均不
  成立，实测 mv x 绝对CFG=PASS），绝对路径下词表改动零暴露 ✓。

## ② tilde × 载体递归——达成

- bash -c / pwsh -Command / cmd /c（含 %USERPROFILE% 展开、S-5 裸形剥词支）/ sudo wrapper×
  载体 / 双层 bash -c 嵌套：tilde 形与绝对形同值（approve/block 全对齐）；深度上限行为与
  绝对形对称（同一既有边界，非本轮新面）✓。
- execute_code 六形态（open('w')/Path.write_text/shutil.copy/os.system/subprocess list）
  tilde 全继承（block/approve 与绝对同值）✓。

## ③ 读写位置语义全链——达成，零误拦反例全锁

- 五形同语义矩阵（tilde/$HOME/单反斜杠/真实绝对/旧别名绝对）× 30 形文件目标写读族：除 mv
  目标一处设计内不对称外全 SAME。`cat/grep/ls` 读位、`cp 源位`、`mv 源位` 恒 PASS——K1/K2/
  K7 构造性成立（视图重写只喂判定管线，读语义由既有矩阵决定）。
- 零扰动：`~/.hermes-agent/...`（前缀名）、`~/.vscode/...`、`/opt/.hermes/...`（家目录外段）、
  `~/x.dat`（无 .hermes 段）全 PASS；视图函数单元行为 10 形逐条正确（含 `~` 本身、双斜杠、
  大小写形归一后命中）。
- 红线四形 on_pre_tool_call 精确复测 4/4：gateway=block、cp 配置绝对形=approve、Copy 源读
  =PASS、-Destination CFG=approve ✓。

## ④ 双代切换集差分（ab33024 代跑 vs HEAD 代跑，39 形矩阵）

- 切换集 **18 形，全部「旁路 PASS→拦截」方向**（tilde/$HOME/%USERPROFILE%/旧别名 × cp/echo>/
  sed -i/tee/-o/-t 粘连/mv 目标/载体递归/截断 .env dd=），零「拦截→放行」回退、零新误拦。
- **但切换集暴露覆盖不对称 → 唯一 finding：** HOME 级宽拦族（cp 目标=home 内**非受保护文件**，
  如 `~/.hermes/x.dat`、`~/.hermes/skills/y.md`、`~/.hermes/`、`~/.hermes/plugins`、`-t ~/.hermes/`、
  rsync/Copy-Item 目录目标）双代同 PASS——绝对形全 approve、tilde 形全漏（见 F-16-S1）。

## F-16-S1（MEDIUM，纳入范围：修不彻底×覆盖不对称——第 7 次同族）

- **位置**：`_judge_terminal_segment` 收集面 4 处 raw-norm↔home 比对点（L1054-1056 is_dir_target
  尾斜杠目录形、L1061-1064 C4 无尾斜杠末位形、L1074 `norm == _hermes_home()`、矩阵 L798/-t 支
  L812-813）+ `_is_protected_config` 的视图只救「清单内文件」不救「HOME 级宽拦」。
- **问题**：round16 视图归一只接进**受保护清单判定**，未接**HOME 级目录目标收集/判定**。凡目标
  落在 home 内但不在配置文件清单（x.dat/skills/logs/cache 非配置名/无扩展名/目录本身），tilde/
  $HOME/旧别名形维持修前旁路，绝对形却拦——正是立项要消灭的「同语义异值」。
- **为什么是缺陷不是既有边界**（三证）：
  1. 纳入范围第 6/7 条：「无尾分隔符目录目标（同语义必防）」「复制/写入目标是守卫目录本体或
     home 内…文件」——绝对形的 HOME 级宽拦是 round5 C4/round4 H-1 在册**防**面，tilde 不继承=
     同一防面两形只存其一；boundary 排除清单四条无一涵盖此形（`cp evil ~/.hermes/x.dat` 是
     朴素一手写形）。
  2. **PM 自己的决策档案（6cd8874，用户裁决 A）认定该宽拦面是「cp+mv 两跳写配置」防御的入口
     焊死**——mv 跳已被本轮修住（`mv x ~/.hermes/cfg`=approve），cp 入口跳 tilde 形仍全开：
     `cp evil ~/.hermes/x.dat`(PASS) + `mv ~/.hermes/x.dat <绝对CFG>`(改名红线 PASS) 两跳到配置
     面落盘。本轮宣称「tilde 面补齐」恰以此设计为目的，入口焊死在 tilde 形只焊了一半。
  3. 修前探针基线矩阵（fix-016.md §0）明记「绝对 cp 目标=approve」为继承面——修后 tilde 形该
     继承未发生，与 §0「段锚定→cp 目标既有处置」的口径相悖。
  - 守卫目录本体形（`cp evil ~/.hermes/plugins/write-guard` 无尾斜杠）实测已 hit（_is_guard_dir_
    target 有视图），缴械面不在此洞；洞在 home 级非清单目录/文件——风险=两跳而非直达，定 MED。
- **修法同构定演（终审猴补丁代跑 `h_patch.py`，被审文件未触）**：收集/判定 5 点把 `norm` 换
  `_protect_view_norm(norm)` 比对，**净改 5 行、零新逻辑**（与 1b/1c 完全同构）。代跑实测：
  13 缺口形 tilde→approve 与绝对同值、2 绝对对照零漂移、8 读位/前缀名/家目录外/绝对 mv 改名
  反例零新误拦。验收建议：pm_verify_017 扩「HOME 级宽拦 tilde 族」靶心 + TC-R17 锁 + 两跳链
  活证（hop1 必须 hit 才算焊死）。

## NOTES（3 条，均不阻断）

- **N-16-1**：alias-mv 目标（approve）vs 绝对-mv 目标（PASS）语义分歧系规格 K3/L4 在册设计，
  建议 CHANGELOG 收线节点名（防后续轮当缺陷重挖）；`ren` 同词表继承该分歧，一并点名。
- **N-16-2**：fix-016.md 纪律核对 4 项复选框未勾（[ ]），其中「未 commit/deploy」与 PM 收线
  commit 事实相容（施工时点未做），「未改 deploy.py/plugin.yaml」等已实测坐实——收线批顺手
  勾齐即可（文档级，round14 也有先例句）。
- **N-16-3**：「代码净增 12 行（≤12）」与 diff 实核（+30/−1、纯代码行 19）之间缺一口径句；
  CHANGELOG 已记 +30/−1 与自纠，建议 fix 制品补一行「12=逻辑插入行（不含 11 行注释/docstring/
  空行）」，与 round15「正则可选项逐词对拍」教训同类（数字口径对拍）。

## 名实对拍小结（质量路焦点）

- 注释承诺 ↔ 字形 ↔ 行为三方：_HERMES_SEG_RE 注释「段边界/前缀名不算/其余零扰动」与正则、
  实测逐词一致（K4/K5/家目录外/`~` 本身全验）；mv 支注释「绝对形 norm==视图维持放行」与
  双闸不可达性一致；disposition docstring 与词表实改一致。TC-R16 12 条编号连续、命名与规格
  T/K 表对应、无死锁形（381=369+12 自洽）。§V 表「实跑回填」4 空位归截断已知缺口（PM 收线
  数字表覆盖，不构成失实）。**唯一名实张力**：CHANGELOG「读/写位置语义、-t/of=/cluster 全族
  判定继承」句——文件清单面继承为真（实测）、HOME 级宽拦面不继承（F-16-S1），「全族」宜收窄
  表述，随修批改。
- 门禁终审独立复跑九项全绿：pm016 16/0、test 29+4+381 ALL PASS、r14 43/0、pm014 29/0、
  pm013 30/0、九 verify 25/28/30/30/46/46/43/53/41 全 0、pm012 零 FAIL、红线四形 4/4、
  部署四镜像 sha 一致 ✓（CHANGELOG 数字与实测逐项吻合）。

## 判级 → 结论

F-16-S1 属纳入范围（同语义必防/朴素写形/在册防御设计的入口半边），按 boundary 判级流程=必修；
修法 ≤5 行同构、零新解析层、灰区标准之外直接命中——**CHANGES REQUIRED**，建议 round17 批
（F-16-S1 五分点 + N-16-1~3 随批 + 决策档案文案缺陷 round17 分支已在册，可并批）。
