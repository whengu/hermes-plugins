# review-018（round18 聚焦终审：三点收紧改对了没——F-17-S1 复验 / bind 否决副作用面 / 双代零漂移亲跑 / 红线+名实对拍）

- **裁决：PASS**（纳入范围内零缺陷；2 条 NOTES 不阻断、不开 round19——复杂度冻结下仅登记）
- 基线：git HEAD=`790049e`（round18=终态基线批 `d727594` 之上仅文档冻结批，代码面
  `git diff d727594..HEAD -- handler.py` 为空）；被审 handler sha[:16]（CRLF 裸字节，
  N-15-1 口径）=`a746cf032c9c4cfa`，工作区 handler.py 与 git 树零差异（--quiet 实测）。
- 对照代：scratch r16=`b58d1d0f21cecb23`（=git 70948f8 亲验同 sha）、r17 代
  scratch LF 形 `0b19915b20999c76` =git 1bcc8cd 亲验同 sha，EOL 归一后
  `0e1e8d4554ac83ff` 与 fix-018 立项批宣称工作树态一致（N-15-1 口径复证）。
- 探针落 `_r2tmp/r18_audit/`（sha4/sha_eol/probe_r18_a_matrix/probe_r18_a2/
  probe_r18_b，git-ignore 内，纯判定零落盘，被审文件未触，未 commit/deploy）。
- 改动面核对（`git diff 0098ebd..d727594 -- handler.py` 亲读，仅 d727594 含代码）：
  1a `_COPY_T_TAIL_RE` 新常量 + 1f 分列支 TAIL 锚 + 注释「前随」→「紧邻前一 token」
  改实；1b 矩阵 -t 支 `_tv != norm` 别名/绝对分闸（绝对维持 f8465c3 search 面）；
  1c `_t_other` bind 否决末位启发（r11 F-10-1 同构）。三点复用同一谓词、零新逻辑、
  零新正则源（TAIL 系 _COPY_T_RE 尾锚变体）——与 fix-018 §A 偏差报告（1f 单点
  22/24 → 三点 24/24）逐点对应 ✓；deploy.py/plugin.yaml 零触碰 ✓。

## ① F-17-S1 复验（round17 表四行全谱 + 长形对偶）——达成

- 四靶心三代（probe A2，HERMES_HOME 钉死真实值）：G1/G3/G6/G7 = r16 PASS → r17
  approve → **r18 PASS**，同语义异值漂移复位 ✓。
- review-017 表第 4 行载体内形补复验（probe B，fix-018 未点名该形）：
  `bash -c 'cp -t /out ~/.hermes/x.dat x'` PASS→approve→**PASS**；pwsh 载体同复位
  （C1/C3）——F-17-S1 全谱（含载体面）封死 ✓。
- 长形对偶（1b 自证）：`--target-directory D:/other/out <tilde源>`（非紧邻）
  approve→**PASS**（C9/S13）；紧邻长形维持 hit（S11）✓。
- cluster 交叠（焦点项）：`-rt` 紧邻 hit（S8）、后随源读 PASS（S9）、
  `-rt D:/out <tilde>` 复位（C7）=方向对偶锁成立；粘连 `"-t…"` 引包支不经收紧
  路径，T6 维持 hit（S12/C11）✓。
- 无 -t 末位零扰动实核：T1~T5/K6 全 hit（S3/S4/C5、TC-R18-10 亲跑）；rsync -t
  分叉三代恒 PASS（G5）；S14 `rsync src ~/.hermes/dest/` r17/r18 同值 approve
  （r16→r17 既存=round16 别名归一族的在册行为，非 round18 引入）✓。

## ② 1c bind 否决副作用面（焦点项）——达成，1 条净变化登记

- 「-t 在场才生效」：S3~S8/S11/S12 hit 全不回退；`install -t D:/out D:/other/bin`
  恒 PASS 无新旁路（S6）；`cp x -t ~/.hermes/out` 紧邻 hit（S7）；tab 紧邻正确
  命中（C12，`\s` 尾锚天然覆盖）；换行=分段不可见，三代恒 PASS 对称（C13）。
- 代价形：`cp -t ~/.hermes/dir x ~/.hermes/dir` 后位否决但首 token 紧邻 TAIL
  命中仍 hit（S5）=§A「不谎称」代价登记属实、无旁路 ✓。
- **净变化一枚（登记 NOTES N-18-1）**：`cp -t D:/out a ~/.hermes/config.yaml`
  （-t 他绑 + 清单文件末位）r16/r17 approve → r18 PASS。机理：清单形经
  `_prot_hit` 恒入收集面（此面未动），判写侧 1c 否决末位启发后其余写门（H-1/
  守卫目录/-t 紧邻/粘连）皆不满足 → 判 False。probe C 钉死绝对对照：同形绝对末位
  （P1）三代恒 approve——tilde PASS/绝对 approve 的不对称系 1b「别名/绝对分闸」
  设计对末位位的延伸（绝对维持既有保守面=review-017 在册「清单面既有保守向」，
  G3 靶心同构先例：规格明文要求 tilde 复位 PASS 而绝对不追平）。GNU 真值该
  token=源位读，r18 方向=FP 消除非新旁路；旧保守收窄一形，冻结裁决下仅登记。

## ③ 双代零漂移亲跑（焦点项：绝对形全量 + 漂移切换集定性）——达成

- 41 形三代矩阵亲跑（probe A2 全表）。r16→r18 切换集 = 12 形，逐形定性：
  G2/G4/G8/S3/S4/S5/S7/S8/S11/S12/S14 = **r16 代无别名/1f 面既有 PASS→approve 向
  （=r16→r17 既存漂移，r18 与 r17 同值=零新增漂移）**——列内 drift17v18 全「-」，
  即 **r17→r18 切换仅 8 形且全为 approve→PASS 误拦复位方向**（G1/G3/G6/G7/S1/S2/
  S9/S13），**PASS→approve 新误拦 0 形**。fix-018 宣称的「G 组转绿+余零回退」实核
  成立（G2/G4/G8/T6/T8/K 零回退 ✓；回退判据=r17↔r18，绝对锚=r16↔r18 于
  A1~A12 全 12 形 + S6/S10/K1~K8/N1/N2 零漂移 ✓）。
- 1b 绝对形维持面专核：A4/A5/A12（绝对 -t 他绑/目标/末位目录）三代恒同值 ✓。
- N-17-2 登记面零变化复证：N1/N2 三代恒 PASS 对称旁路维持 ✓。

## ④ 红线 + 名实对拍——达成

- 红线探针（PM 随批 + 复审独立复跑）：probe_018_redline 9/9 ALL-OK（gateway
  block、cp 配置 approve、Copy-Item 源读 PASS/-Destination approve、\tmp block、
  紧邻/cluster/-rt 后随源读对偶、mv 别名目标 approve）✓。
- 全链门禁独立复跑（不采信 §D 自报）：test_handler ALL PASS 29+4+404；九 verify
  25/28/30/30/46/46/43/53/41/43 全 0（与 CHANGELOG 宣称数组**逐位全等**）；
  pm012 零 FAIL、pm013 30、pm014 29、pm016 16、pm017 19/0、pm018 24/24 ✓。
- 名实抽查：§A「TAIL 锚/分闸/bind 否决、零新逻辑」与 diff 逐行一致；TC-R18 10 条
  断言与宣称逐条对应；CHANGELOG round18 节数字（22/24→24/24、404、verify 数组、
  N-17-1~4 随批、第八次名实登记句）实测全符；pipeline-status round18 节与
  冻结节口径一致；决策档案含用户「终审不可跳过」补充纠正段（本审即其执行）。
- **一处文档名实微瑕（NOTES N-18-2）**：CHANGELOG 门禁行「红线四形+write_file+
  rm -r 分层 6/6」沿用旧口径句，round18 实际红线工件为 9 形版（§D 表所列），
  数字 6/6 系沿 round15 句式未随批更新——不谎称方向（实际 9/9 更强），仅陈旧
  表述，登记不阻断。

## 结论

**PASS**。round18 三点收紧改对了：F-17-S1 四靶心+载体+长形全谱复位、bind 否决
副作用面零新旁路零误拦（切换集 8 形全为复位向）、绝对形双代零漂移亲跑坐实、
红线与全链门禁独立复跑全绿、制品-代码-宣称三方名实相符（一处陈旧句式入 NOTES）。
N-18-1/-18-2 两条 NOTES 在冻结裁决下仅登记，不开 round19。round18=终态基线成立。
