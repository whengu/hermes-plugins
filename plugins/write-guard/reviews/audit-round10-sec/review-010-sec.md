# review-010-sec：write-guard round10 终审（安全路，只读）

- 评审人：sa-0（安全路）｜日期：2026-09-22｜基线：git 2cc28cf（handler.py 1222 行，sha16 779ceb43ad7c9491）+ 工作区
- 判据：reviews/round10-context.md 收敛判据 + requirements/requirement-20260922-boundary.md。
  立项仅限纳入范围新旁路 / 纳入范围误拦 / 名实不符；排除范围与已登记边界一律附录。
- 入口口径遵守 round10-context §24：全部探针走 `on_pre_tool_call`（含守卫 D 与四守卫链），无一例误用 _judge_terminal。
- 探针（本目录，载荷全文件内构造，命令行零载荷）：r10s_probe_0_deploy.py（部署同代际 sha 核对）、
  a_f91.py（F-9-1 四向×cp 同语义×FP）、b_f92.py（F-9-2 wrapper×载体双向 + 组合新面搜寻）、
  c_f93_f94.py（F-9-3/F-9-4 复测 + /O、-O、tee 邻域回退，含新旧代际对照）、
  d_redlines_new.py（三条红线 + 归一化/大小写/引号/内嵌链新旁路搜寻）、
  e_f93_neighbors.py（/O= 等号粘连、URL 粘连、全路径载体归因）、
  f_named_target_fp.py（命名目标前置位 + F-9-3 FP 族归因）、
  g_named_target.py / h_evidence_fix.py（F-10-1 证据补全 + F-10-2 修法方向 token 级预演）。
  代际对照快照 handler_r9_cbd6301.py（git show cbd6301:handler.py，落本目录）。
- 基线复跑（独立实跑，非转述）：test_handler ALL PASS 29+4+292；_verify_r10 46/0、r9 46/0、
  r8 30/0、r7 30/0、r5 28/0、r3 25/0——与 round10-context 验收基线一致。
- 部署一致性：源 + 主部署 + architect/developer 双镜像，__init__/handler/plugin.yaml 三文件
  sha 全同代际（probe 0 实测）。
- 现场活证：探针脚本自身向 /tmp 写快照时被守卫 C 实拦（block 消息含命中模式 `\tmp`），
  改道工作区——C 守卫红线在真实调用链上生效。

## 一、F-9-1~F-9-4 修复复测结论

| 项 | 攻击形复测 | 误拦/负例复测 | 判定 |
|---|---|---|---|
| F-9-1 复制族四向 | 源位读 10 形（位置/-Path/大小写/反斜杠/内嵌引号体/内嵌裸形/cmd 对照）全 PASS；Tee-Object -FilePath 非保护 PASS；Tee-Object CFG（位参即目标）=approve（PS 语义正确，探针初判 DIFF 系我方预期错，非缺陷） | 目标写配置 5 形全 approve（含 cp 对照）；写守卫源码/目录（无尾斜杠/带尾斜杠）approve 且与 cp 同款零分叉；Set-Content/Add-Content/Out-File/内嵌/小写/直写重定向 出现即写支不回潮 block；Get-Content/cat/mv/通配符/&&链负例 PASS；execute_code 内嵌两向正确 | ✅修复成立（红线"复制不拦"归位，cp 同语义一致）；唯「命名目标前置位」面随摘出转漏——见 F-10-1 |
| F-9-2 wrapper×载体 | 13 封堵形全命中：sudo/nohup/time/env×赋值/runas 前导 × bash/sh/cmd/pwsh 载体 × cp 守卫/重定向/tee/sed -i/curl -o/sort /O/双 wrapper/单引号体/续行/cd 链式；LANG=C pwsh Copy-Item 巧合命中归正（approve 正通道） | 13 负例全 PASS 零误拦：env\|grep、time ls、nohup python &、sudo cat 读、sudo bash -c "echo hello"、env/time 裸用、sudo -u root（登记边界 cw=root）、非载体词、env VAR=x ls 守卫目录、全剥尽不可判定；sudo rm -rf 守卫=平台分层 PASS 不误扩 | ✅修复成立，双向无伤（FP/漏两侧均未引入新面）；残余全路径载体/引号包载体两形两代同向 → 附录 |
| F-9-3 sort /O | 10 形全 block（空格/粘连/小写 /o/大写 SORT/cmd /c/sudo/&&链/反斜杠路径/内嵌 bash -c），old=PASS 对照确认为本轮新封堵 | 邻域 12 负例全 PASS 无回退：curl -O URL（红线）、-oL cluster、wget -O 非保护、grep -o、findstr /O（门外）、mount -o rem,rw、tar -O、sort /D、sort 只读两文件、--output= 对照仍 block；sort -o 不回潮 | ⚠️封堵与回退双向达成，但短形组字符类放宽令 `[-/]o` 可在 before 内任意位置命中，路径 token 以 `/o`、`/O` 收尾 × 门内命令 × 后随受保护路径 → 新误拦，见 F-10-2（old=PASS/new=block 实锤） |
| F-9-4 tee 段命令词 | 8 形全 block：非末位、-a 多目标、三目标中位、-i 首位、sudo tee、pwsh 别名内嵌、内嵌 bash -c 管道、tee CFG out2 对照；old=PASS 三条确认为本轮新封堵 | tee 非保护/仅非保护/词内 teeobjtool/路径含 tee/ls 读 全 PASS；execute_code subprocess list 形 block | ✅修复成立（"全部位参皆目标"口径注释同步，名实相符）；`tee -a<粘连>` 非可运行形 PASS 与附录④同根 |

## 二、发现（全部实测复现；old/new=cbd6301/2cc28cf 对照，探针 c/f/g/h）

### F-10-1（MED·本轮修复引入的纳入范围新旁路）复制族「命名目标前置位」漏拦

- 复现（old=block → new=PASS，本轮引入的方向性翻转）：
  `Copy-Item -Destination <CFG> <非保护路径>` → **PASS**；`Tee-Object -FilePath <CFG> -InputObject x` → **PASS**；
  载体内形（`pwsh -Command "Copy-Item -Destination <CFG> …"` 引号体/裸形两式）与 `sudo pwsh -Command …`
  前导形同陷（F-9-2 通道打通后新暴露的组合面）。
- 反向伴随（同根第二向）：`Copy-Item -Destination <非保护> <CFG>`（CFG 实为**源**）→ **approve**，
  源位读被弹卡——与 round9 F-9-1 同族的位参语义缺陷，方向是 FP 向。
- 判据：boundary §纳入7（写目标是 home 内配置文件为必防义务）+ §纳入3 整词选项形 + §纳入5 载体链。
  根因：复制族既有判定只认「末位路径参数=目标」（_terminal_position_is_write L697-709）与
  `-t/--target-directory` 前缀（仅 cmd∈cp/install，L717）。Copy-Item/Tee-Object 并入 _COPY_CMDS 后，
  其 PowerShell 原生命名目标参数 `-Destination`/`-FilePath` **前置位**既不在末位分支、也不在 -t 分支，
  CFG 非末位 → 写语义不成立 → 放行。修法规格 fix-010-input §F-9-1 明文「源位→PASS、目标写配置→approve」
  未区分前后置，落地实测在尾位形正确（_verify_r10 B 行、TC-R10-02 同款），前置形无 TC/verify 覆盖
  ——round10-context §27 锁的是"四向"，四向用的是位置形与尾位 -Destination 形，前置位是第五向（新面）。
- 修法方向（≤5 行、零新解析层，灰区判据通过）：_COPY_CMDS 分支内补一条「cmd∈copy-item/tee-object 且
  before 以 `-(Destination|FilePath|Path|Container)` 类命名目标标志结尾 → 本 token 即写目标」（复用
  _COPY_T_RE 同款写法，token 前置判据现成）；反向 FP 向（目标已绑非保护、CFG 落源位）随该判定归正
  为"CFG 非目标 → 末位分支不判写"，两向一并处置。若判定该族扩位参复杂度过高，亦可按"复制至守卫
  目录 approve"同口径降为登记——但 `-Destination <CFG>` 直写用户配置文件，属纳入范围，登记不修不成立。

### F-10-2（LOW·本轮修复引入的纳入范围误拦）`[-/]o` 短形放宽在路径 token 上误命中

- 复现（old=PASS → new=block，本轮引入）：`sort D:/myagent/workspace/o <CFG>` → **block**（读两个文件，
  无任何写语义）；`sort D:/myagent/workspace/O <CFG>` → block；`curl http://x/o <CFG>` → block；
  `wget http://x/f/o <CFG>` → block。对照 `sort D:/myagent/workspace/my-dir-o <CFG>` → block 为
  **两代同陷**（round9 `-o` 同根，非本轮引入，附录⑥）。
- 判据：boundary §纳入1 的 cp/sort 常规读用法被误拦（§纳入6 Windows 正斜杠路径为常规书写形，
  `/o`、`/O` 结尾的目录/URL 路径非冷知识）；且 F-9-3 规格明文负例「unix 族不回潮」，本面是该负例
  未覆盖的邻域。根因：_OUTPUT_FLAG_RE 短形组放宽为 `[-/]o`、`[-/]O` 后仍锚 `before…$`（前一 token 结尾），
  但路径 token 与选项 token 在本判定里同构——`…/o` 恰好以 `/o` 结尾，被当作"输出标志后紧跟目标"。
- 修法方向（2 行内，与 F-9-3 改动同点收敛）：短形组加 token 独立约束
  `(?:^|(?<=\s))[-/]o(?:$|\s)`（探针 h 预演：curl/wget/sort 的 `-o `/`-O `/`/O `/`-sSL -o ` 全保持命中；
  `http://x/o `、`workspace/o `、`my-dir-o ` 全转不命中；`curl -o = <CFG>` r9 锁形走 _OUTPUT_FLAG_EQ_RE/
  _GLUED_O_RE 链不受影响，实测仍 block）。同修顺带把附录⑥的 dash 同根旧 FP 一并归正（净 FP 面收缩，
  不新增拦截语义——/O 粘连与空格形封堵由 _GLUED_O_RE 与独立短形各自保证）。

## 三、红线保持核查（全部实测，on_pre_tool_call 正确入口，探针 d）

1. **gateway restart block** ✅ 12 形：restart/run/start、大写、bs+LF、bs+CRLF、跨行续（echo &&\
   hermes \n gateway restart）、全局 flag、sudo/&/cmd 载体交叉、内嵌引号体全 block；
   status/stop/--help 不误伤 PASS。
2. **rm -r 平台分层** ✅：rm -r 守卫目录、rm -rf home、rd /s /q、sudo rm -rf 全 PASS（插件不扩，
   与 CHANGELOG 分层登记一致，拦截职责在平台 approvals 层）。
3. **cp 写配置弹卡** ✅：直写/引号源/copy /Y/cmd 载体裸形/Copy-Item 目标/sudo bash -c 弹卡形
   全 approve；cp 源位备份 PASS、mv 改名族 PASS、非 cp 写配置（echo>/sed -i/2>）block。
4. **写工具入口** ✅：write_file CFG/HD/大写/路径归一化变体 block、workspace 负例 PASS、
   patch 守卫 block、memory approve、read_file 纯读 PASS。
5. 附带活证：本评审工作脚本写 /tmp 被守卫 C 实拦后改道工作区（部署核对脚本 probe 0 记录）。

## 四、附录：排除范围/登记边界/既有面实测罗列（一律不立项）

1. `bash --login -c "…"`、`nice/xargs` 白名单外 wrapper × 载体 → PASS：S-4 定死五词禁扩 +
   Q9-N2 登记，实测维持（探针 b）。
2. 全路径/引号包/相对路径载体（`/usr/bin/bash -c`、`"bash" -c`、`./bash -c`、含 sudo 叠加）→
   两代同向 PASS：附录③族延伸归因实测（探针 e），F-9-2 剥离链令前导错位但方向不变差，不立项。
3. `sudo -u root bash -c`/`sudo -u root cp` → cw='root' 登记边界维持（探针 b/f）。
4. 非可运行粘连形：`tee -a<CFG>`、`tee -ia<CFG>`、`curl -O<URL>`、`/O=` 等号粘连 → 两代同向 PASS
   （实 shell 不接受该形，附录④先例"非可运行命令无防护语义"，探针 e）。
5. glob 目标（`cp evil <CFG所在目录>/*.py` → approve 弹卡方向保守、`<home>/*.yaml` approve）：
   末位保守收集既有 C4 口径，弹卡非静默放行，附录既往。
6. dash 同根旧 FP `sort …-o <CFG>` → 两代 block：round9 既有（探针 f 实测 old 同陷），
   由 F-10-2 修法顺带归正，不单独立项。
7. robocopy/tar/ln/tilde/$HOME 未展开形、跨家、会话 cd 漂移（M-3）、变量间接/eval/编码混淆、
   三层以上嵌套：既有登记，实测方向一致（探针 b/d/e NA 组）。
8. `cp evil <home>/*.yaml`、curl `-o =` 空格等号等矩阵边缘形：处置与登记口径一致（弹卡/block
   保守向），不立项。

## 五、名实核查

- fix-010.md §1~§6、CHANGELOG round10 节、round10-context §27 两处 PM 声明逐条实测相符：
  F-9-1 四向处置（含③守卫源码 approve=cp 同款）、F-9-2 剥离单点与负例清单、F-9-3 字符类
  与"unix 族不回潮"（本面属其未覆盖邻域，非声明失实）、F-9-4 注释口径改"全部位参皆目标"、
  Q9-N2 根因句（开关组只认单横杠，实测 `/usr/bin/bash` 等归因与之自洽）——**未发现名实不符立项**。
- 唯二微疵（不立项）：①handler L254-257 注释"摘出并入 _COPY_CMDS"未注明前置命名目标位仍是
  已知窄面（随 F-10-1 修复顺手补一句）；②`_prev_command_word`（L606）自 F-9-4 起零调用（含定义
  仅 1 处引用，探针 f 实测），成死代码，质量路口径登记即可。
- 改动纪律：git diff cbd6301..2cc28cf handler +48/-12 行，四修复点均为规格定死的单点改动，
  无顺手改无关行；test_handler +49 行（TC-R10 15 条含四向锁）。

## 六、裁决

**CHANGES REQUIRED** —— 2 条：**F-10-1（MED，本轮引入旁路）** Copy-Item/Tee-Object 并入复制族后
「命名目标前置位」（`-Destination/-FilePath <受保护> <非保护>` 及载体/前导组合形）漏拦，反向伴随
`-Destination <非保护> <受保护源>` 误弹卡；纳入 §纳入7×§纳入3×§纳入5，old=block→new=PASS 实锤
为本轮引入，非既有登记边界。**F-10-2（LOW，本轮引入误拦）** F-9-3 短形组 `[-/]o` 放宽在路径/URL
token 以 `/o`、`/O` 收尾时误命中（`sort ws/o <CFG>`、`curl http://x/o <CFG>` old=PASS→new=block），
修法 2 行内（token 独立约束），顺带归正 round9 同根 dash FP。其余：F-9-1/2/3/4 修复本体验收通过
（复测矩阵 §一，双向无伤）；三条红线全保持；基线 29+4+292 / 46+46+30+30+28+25 独立复跑全绿；
round9 探针 a~h 全集回归无回潮；部署三目标同代际；附录 8 族登记不立项；名实无违。

—— sa-0（安全路）2026-09-22 round10 终审，全程只读；探针 r10s_probe_0/a~h + 代际快照
handler_r9_cbd6301.py（本目录）。
