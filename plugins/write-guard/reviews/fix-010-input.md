# fix-010 修复规格（round10：安全路 F-9-1~F-9-4 + 质量路登记项）

基线：git cbd6301（round9 已部署），277 new 用例 ALL PASS。
最高准绳不变：requirements/requirement-20260922-boundary.md。
所有 finding 均 PM 独立实测复现（reviews/fix010-scratch/pm_verify_010b.py 输出为准）：
A/B/C=block、E=PASS、G/H/I/J=PASS、K=block、L/M=PASS、N=block、O=PASS、P=PASS、Q=block。
每项修法已定死（报告 review-009-sec.md §二给出），**禁止扩范围、禁止重构、禁止顺手改无关行**。

## F-9-1（MED·红线相关，最高优先）Copy-Item/Tee-Object 摘出「出现即写」支
- 现状（实测）：`Copy-Item <CFG> <BAK>`（源位读）→ **block**，违背红线"复制不拦"
  且与 `cp CFG BAK`（PASS）同语义分叉；`Copy-Item <BAK> <CFG>`（目标写配置）→ block，
  与 `cp BAK CFG` → approve（cp 写配置弹卡红线）分叉。
- 修法：`_PS_WRITE_RE` 词表拆两组——
  Set-Content/Add-Content/Out-File 保持现「受保护路径出现在 cmdlet 后=写」支不变；
  Copy-Item/Tee-Object 摘出，命中后并入 `_COPY_CMDS` 同款路径（末位/命名目标判定：
  源位→PASS、目标写配置→approve 弹卡、目标写守卫文件→block、复制至守卫目录→approve，
  完全复用既有复制族处置，零新判定逻辑）。≤6 行 + 1 行词表拆分。
- 注释同步：_PS_WRITE_RE 处注释名实改写（现注释暗示五词同支）。

## F-9-2（MED）wrapper × 载体前导组合
- 现状（实测）：`sudo bash -c "cp evil <GD>"` → PASS；`LANG=C pwsh -Command Copy-Item…`
  靠 _PS_WRITE_RE 巧合命中（通道未打通的伪装覆盖）。
- 修法：新增小 helper `_strip_wrapper_prefix(seg)`（≤6 行）：把 _command_word 剔除链
  （_COMMAND_WRAPPER_RE / _ENV_ASSIGN_RE / 前导选项词）复用为**返回剩余文本**；
  _EMBED_SHELL_RE 与 _BARE_CARRIER_RE 匹配前先对该 helper 的输出尝试匹配（匹配对象
  用剥离后文本，命中后 body/rest 提取逻辑不变）。若一处改动可行则单点改在
  _judge_terminal_segment 载体识别入口处（推荐，避免两正则各改）。
- 负例必测：`env | grep config`、`time ls`、`nohup python x &` 不回退；
  `sudo cmd /c copy evil <CFG>` → approve（复制族）；`sudo bash -c "echo x > <CFG>"` → block。

## F-9-3（LOW）cmd 原生 sort /O 输出位参方言
- 现状（实测）：`sort /O <CFGS> d.txt`、`sort /O<CFGS>`、`SORT /O`、`cmd /c sort /O…` 全 PASS。
- 修法：`_OUTPUT_FLAG_RE` 与 `_GLUED_O_RE` 两处字符类 `^-` → `^[-/]`（报告核定 ≤6 行、
  灰区通过；_command_word 对 `sort /O x d` 提取 'sort' 已实测不受影响）。
- 负例必测：`findstr /O x f`（门外的未知/非输出族命令不误拦——按门的既有语义）、
  unix `-o`/`-O` 全族不回潮；`sort -o <CFG>` 仍 block。

## F-9-4（LOW）tee 多文件位参非末位
- 现状（实测）：`echo x | tee evil.txt <CFG>`、`tee -a evil.txt <CFG>` → PASS；
  `tee <CFG> out2` → block。别名形 `pwsh -Command "tee evil <CFG>"` 亦 PASS
  （与词表登记不同根——位参矩阵缺陷；F-9-2 通道打通后应自然命中）。
- 修法：`prev == "tee"` 判据改为"段命令词 == tee"（_command_word 现成，≤2 行）。
- 注释顺手改："tee 目标→写" 补"（全部位参皆目标）"口径。

## 登记与文档项（随批，不动逻辑）
- Q9-N1：CHANGELOG 附录③族补一句"全路径命令词（/usr/bin/ls cp …）两代同向 PASS，
  登记不修"（PM 实测背书）。
- Q9-N2：CHANGELOG 补登记句"`bash --login -c \"…\"` 双横杠长开关打断载体识别，
  既有面登记不修"（若 F-9-2 的剥离 helper 顺带覆盖则改锁向为命中，实测为准）。
- Q9-N3：round9 节"每项 ≤6 行"总括与 S-4 实际（体重写+2 正则）口径修正为"每处改动
  核心逻辑 ≤6 行，S-4 含替换体重写"。
- N1 句（round8 节）"暂无 TC 场景，补锁向列入收尾"如与 round9 已闭环句冲突，以闭环为准微调。

## 过程与制品纪律（硬红线）
1. 先建 reviews/fix-010.md 骨架（§0 行为映射 / §1~4 各 F 落地 / §5 登记 / §6 验收），
   每步立即落盘带 [DONE F-9-x] 标记。
2. 改动脚本先 compile 再落盘（原子纪律）；锚点先 grep 现场确认。
3. test_handler.py 新增 TC-R10：每 F ≥1 封堵/归正锁 + ≥1 负例；F-9-1 必须四向锁
   （源位 PASS / 目标写配置 approve / 目标写守卫 block / cp 对照不变）。
4. 新建 _verify_r10.py（含 pm_verify_010b 同场景翻转断言 + 回归负例全集）。
5. CHANGELOG round10 节 + 上述登记项。
6. 验收八项实跑贴末行：test_handler / _verify_r10 / _verify_r9 / _verify_r8 / _verify_r7 /
   _verify_r5 / _verify_r3 / pm_verify_010b（预期：A/B/C 转 PASS 或 approve 按红线方向、
   F=approve、E=PASS、G/H/I/J=block、K=block、L/M/O=block、N=block、P 命中(approve)、
   Q 经正通道命中）。
7. **不要 git commit、不要 deploy**。
8. 终答 ≤250 字：八项验收末行 + 改动文件 + 每 F 一句处置。所有验证载荷落 .py 文件。
