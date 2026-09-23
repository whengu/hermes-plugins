# review-017（round17 聚焦终审：wide_landing 分流谓词误分面 + T6/T8 补点语义分叉 + 绝对形双代零漂移复证 + 门禁全链名实复跑）

- **裁决：CHANGES REQUIRED**（1 项纳入范围缺陷 F-17-S1——round17 补点 1f 引入源位误拦，
  ≤2 行修法已猴补丁定演；4 条 NOTES 不阻断）
- 基线：git HEAD=`1bcc8cd`（round17 PM 收线批）；被审代码面 `handler.py`
  sha256[:16]（CRLF 裸字节，N-15-1 口径）=`0e1e8d4554ac83ff`；修前基线 `70948f8` 态
  =`b58d1d0f21cecb23`（git show 导出 `_r2tmp/r17_audit/h_base.py`）。
- 探针落 `_r2tmp/r17_audit/`（probe_r17_a/b/c/d/e/g/h/i/j + h_fixdemo.py 猴补丁面 +
  pm017_on_fixdemo.py，git-ignore 内，纯判定零落盘，被审文件未触，未 commit/deploy）。
- 改动面核对（`git diff 70948f8..HEAD -- handler.py` 亲读）：改动1 五比较点接视图
  （L810 H-1 尾分隔支 / L823-826 矩阵 -t 支 `_tv` / L1070-1073 is_dir_target `_v` /
  L1079 C4 支 / L1102 `_v==home`）+ 补点 1f（L1090-1098）+ 改动2 文案三支（新模板/
  `_approve_result` template 形参 / `_config_write_disposition` wide_landing 形参 +
  收集处 4 元组）——与 fix-017-input 规格逐点对应，零扩面；deploy.py/plugin.yaml 未触 ✓；
  部署四镜像 + 工作区 handler 全 `0e1e8d4554ac83ff` 一致 ✓。

## ① wide_landing 分流谓词误分面（焦点项）——达成，边界两枚登记 NOTES

- 谓词组合九格全遍历（probe_a）：`prot∧带点→CONFIG`、其余→WIDE，无第四象限意外。
  端到端文案现形 21 形（probe_a/f）：M1 在册形（skills/safe-config-modify→WIDE）、
  M2 真配置（config.yaml/.env/plugins 代码→CONFIG）、宽拦七变体（x.dat/skills/日志/
  home 本体/无扩展/cfg/绝对对照）全 WIDE 且与规格「清单真配置=受保护∧带扩展名点号」
  宣称逐一对齐；`safe-config-modify` 这类目录名含 config 子串者正确落 WIDE（谓词
  prot_hit=False，双保险形态位亦不触发）✓。行为零变化复证：分流只喂 `_approve_result`
  模板位，action/rule_key/判定链不可达（代码走读 + ③ 双代零漂移矩阵共证）。
- 张力两枚见 NOTES N-17-3/N-17-4（均文案级、不谎称、不阻断）。

## ② T6/T8 补点 × rsync/分列 -t 语义分叉（焦点项）——方向达成，但引入误拦 → F-17-S1

- 正向矩阵（probe_c/e/h）：rsync -t 全族语义分叉守住——`rsync -t ~/.hermes/config.yaml
  dest/`、`rsync -t ~/.hermes/tdir dest/`、`rsync -t <CFG> dest/` 双代恒 PASS（R4-1
  锁不压平）；`rsync src ~/.hermes/dest/` tilde 形转 approve 与绝对形 R6 对齐（末位
  目录目标=复制族既有语义，非 -t 面）✓；install 族对齐（R10/I-a hit）✓；载体内
  （bash -c/pwsh -Command/cmd /c %USERPROFILE%）全 hit ✓。
- 1f 门控三条件实核：仅别名形（`_v≠norm`）到达——绝对 `-t` 双代恒 PASS 零漂移
  （L8/L12/W2 复证）✓；rsync 不入（cmd 门 cp/install）✓；粘连支 `_GLUED_T_RE` 经
  `_pair_unquote` 引号整包正确（S2 裸粘连/L11 `-t=` 形/T6 引包全 hit）✓。
- **但分列支 `_COPY_T_RE.search(seg[:m.start()])` 为段内任意位置搜索，非「-t 紧邻本
  token」绑定** → 见 F-17-S1。
- 残留旁路定性（probe_i Q1-Q6）：`cp '-t' ~/.hermes/tdir x`（引号选项词分列）、
  `cp "--target-directory"=~/.hermes/tdir x`、`cp "-rt" ~/.hermes/tdir x` 双代同
  PASS——绝对形亦双代 PASS=**对称既有边界非本轮回归**（纳入第 4 条的引号选项词族
  宽拦面两形皆漏，round5 C3 域旧账；归 N-17-2 登记，不作本轮 finding）。

## F-17-S1（MEDIUM，纳入范围——round17 补点引入的源位读误拦，同语义异值反向）

- **位置**：`_judge_terminal_segment` L1097-1098（1f 分列支）。
- **问题**：`cp -t <HOME 外目标> <tilde 源> <末位>`——源位 token 本应读红线放行，
  实测被 1f 以「段内任意 -t 存在即视为本 token 绑定」收入收集面，复经矩阵 F-A7 支
  （同款非锚定 search）判写：

  | 形（probe_g/i/h） | 基线 70948f8 | HEAD |
  |---|---|---|
  | `cp -t D:/other/out ~/.hermes/tdir x`（源=目录读） | PASS | **approve（FP）** |
  | `cp -t D:/other/out ~/.hermes/x.dat evil`（源=文件读） | PASS | **approve（FP）** |
  | `cp -t D:/other/out D:\…\.hermes\x.dat evil`（绝对同形） | PASS | PASS |
  | 载体内同形 `bash -c 'cp -t /out ~/.hermes/… x'` | PASS | **approve（FP）** |

  绝对形/tilde 形同语义异值（误拦向）；且 `search(before)` 非锚定在绝对面被 prot_hit
  收集链掩盖（G6 双代恒 approve 系清单面既有保守向，非本 finding 面）。
- **为什么是缺陷不是既有边界**：①用户红线「复制源位=读不拦」（K7 族在册锁）；
  ②boundary 纳入第 3 条「整词引号包裹路径」常规形；③误拦向按判级流程 +
  「零误拦优先」=必修；④**本轮新引入**（双代差分实锤 PASS→approve，A 组绝对形
  0 切换共证非环境漂移）——与 round13 教训「词表收窄压平一维语义」同构第四次：
  「前随标志存在」与「标志绑定本 token」两维被 `search` 压平。
- **修法定演（猴补丁 `h_fixdemo.py`，被审文件未触，≤2 行）**：分列支改紧邻锚——
  `seg[:m.start()].rstrip()` 须以 `-t` 短形/cluster/`--target-directory` 长形收尾
  （`_COPY_T_TAIL_RE = (?:\s|^)-[a-zA-Z]*t(?![a-zA-Z])$|(?:\s|^)--target-directory$`）。
  代跑实测：**11 靶心锁全保持**（T6/T8/L7/L9/L11/S1/S2/E3/R10/I-a/T7 = hit，pm017@
  fixdemo **19/0**）；G1/G3 误拦形转 PASS 与绝对对齐；G5（源=config 清单面）维持
  approve=与绝对形 G6 同语义对齐（保守向既有面，非回归）；红线七形三代表全一致
  （probe_j：gateway block/cp 配置 approve/Copy 源读 PASS/-Destination approve/
  rm -r PASS/write_file block/mv 绝对改名 PASS）。
- **验收建议**：round18 批——pm_verify_017 扩 G1/G2/G3/G4 双代对齐靶心 + TC-R18
  锁（源读红线 × `-t` 他处形）；修法即锚定收紧，禁扩新逻辑。

## ③ 绝对形双代差分零漂移复证（焦点项）——达成

- 39+ 形大矩阵（probe_d：A 绝对 26 形 / T tilde 20 形 / C 锁 18 形）：
  **A 组切换 0**（cp/-t/长形/mv 改名/echo/tee/sed -i/sort -o/curl -o/wget/truncate/
  rsync/shutil 绝对形双代逐形同值）；**T 组切换 12 形全部「PASS→approve」拦截向**，
  零放行回退（$HOME 形走既有清单链本就覆盖、载体三壳继承、`cp a b ~/.hermes/dest`
  多源非末位=绝对同值 parity 达成）；C 组唯一「违规」形 `cp evil C:/Users/guwh/.hermes/x.dat`
  实为 **tilde 的绝对同形**（旧别名=段锚定靶心，PASS→approve 系设计内，probe 分类
  误置非代码缺陷）。零误拦锁 17 形双代恒 PASS（读位/源读/改名/前缀名 .hermes-agent/
  `~/.vscode`/`/opt/.hermes`/`~/x.dat`/rm -r 分层）。
- 两跳链端到端（probe_f）：hop1 五形入口全 hit（含 `-t~/.hermes` 粘连与载体内），
  hop2 绝对改名三条恒 PASS——链断在入口，不扩 mv 面 ✓。
- $HOME/%USERPROFILE 展开链实测继承（E1/E2/E3 → approve，_expand_env 步 1 生效）。

## ④ 门禁全链复跑 + 名实对拍（焦点项）——数字全绿、宣称逐句核

- 终审独立复跑（HEAD 0e1e8d45 面）：pm017 **19/0**、pm016 **16/0**、pm014 **29/0**、
  pm013 **30/0**、_verify_r14 **43/0**、九 verify **25/28/30/30/46/46/43/53/41 全 0**、
  pm012 grep FAIL=**0**、test_handler **ALL PASS (29+4+394)**、红线四形+扩七形 4/4+7/7、
  部署四镜像 sha 一致——与 CHANGELOG round17 节「|…|」数字行逐项吻合 ✓。
- TC-R17 13 条走读（run_r17_fixes）：编号连续、断言值与 pm017 表同构、注册入链
  （1646-1647 行）；TC-R17-10 绝对 -t 零漂移锁与 K9 双锁在位。
- 名实三方对拍：改动2 注释「清单真配置=受保护∧带扩展名点号」↔ 实现 `not (_prot_hit
  and "." in _fn)` ↔ 实测一致 ✓；改动1 注释「绝对形 norm==视图恒零漂移」✓（③ 复证）；
  **一处失实**见 N-17-1（1f 注释「分列形=前随 _COPY_T_RE」——「前随」承诺 vs `search`
  段内任意实为两回事，即 F-17-S1 根因，第八次名实登记）。

## NOTES（4 条，均不阻断）

- **N-17-1**：fix-017.md §0 句「`cp "--target-directory=~/.hermes/tdir" x` 引号前缀
  变体经收集位 norm_raw 提取支（L1025）无末位约束已通」失实——实测该变体双代恒 PASS
  （提取支产 norm 后仍被 is_dir_target/C4/1f 收集门槛拒收：值无尾分隔符、非末位、
  非清单）。绝对形同串亦 PASS=对称既有旁路（round5 C3 域），非本轮回归，但制品句
  须就地改实（名实现象第八次：把「提取支可达」写成「已通」——宣称覆盖必须落到端判据）。
- **N-17-2**：引号选项词族 `-t` 宽拦面双代同漏（`cp '-t' ~/.hermes/tdir x`、
  `"--target-directory"=~`、`"-rt" ~` 三形，probe_i Q1/Q3/Q5；绝对同形 Q2/Q4/Q6 亦
  PASS）——对称旁路按「修不彻底×覆盖不对称」判据不构成本轮 finding，建议 round18
  随批入 CHANGELOG 接受边界或补登（纳入第 3/4 条交叠灰区，5 行内可修则做的旧判例可援）。
- **N-17-3**：rule_key 以 norm（非视图）为键（L597 消费 4 元组 norm 原值）——同物理
  文件的 tilde/绝对别名弹卡键不同（`c:/users/guwh/.hermes/x.dat` vs
  `d:/myagent/.hermes/x.dat`），批准记忆跨别名不互认。双代一致=round16 既有继承面非
  本轮引入；文案展示位 `_shown_path` 不受影响。登记在册防后续当缺陷重挖。
- **N-17-4**：分流谓词形态位（`.` in filename）的边缘：`cp a ~/.hermes/config`
  （名含 config 无扩展=清单真配置）得 WIDE 句——文案仍真实自解释（「落位审批…防两跳」
  对配置目标亦成立），规格明载「带扩展名点号」双保险系 PM 实测 `safe-config-modify`
  命中谓词后的在册取舍；不扩锁建议：接受边界注一句。

## 判级 → 结论

F-17-S1 属纳入范围（源位读红线 + 误拦向零误拦优先 + 本轮新引入实锤双代差分），
修法 ≤2 行锚定收紧、零新逻辑、定演面 pm017 19/0 + 11 锁零回退 + 红线七形三代表零差
——**CHANGES REQUIRED**，建议 round18 小批（F-17-S1 + N-17-1 改实 + N-17-2 登记随批；
①③④ 三焦点全达成，改动1 五分点/改动2 分流/门禁链/零漂移宣称均复证实至名归）。
