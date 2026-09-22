# review-009-sec：write-guard round9 终审（安全路，只读）

- 评审人：sa-0（安全路）｜日期：2026-09-22｜基线：git cbd6301（handler.py 1198 行，含 S-1~S-5）
- 判据：reviews/round9-context.md 收敛判据 + requirements/requirement-20260922-boundary.md。
  立项仅限纳入范围新旁路 / 纳入范围误拦 / 名实不符；排除范围与已登记边界一律附录。
- 探针（本目录，载荷全文件内构造，命令行零载荷）：r9s_probe_a.py（S-1 复测+邻域新搜寻）、
  r9s_probe_b.py（S-2 复测+S-4 剔除影响面/词提取观测）、r9s_probe_c.py（S-3 双向+FP 重点：
  URL 内 & / 2>&1 / >NUL / split trace）、r9s_probe_d.py（S-5 复测+round8 探针全集回归+gateway）、
  r9s_probe_e.py（三条红线+写工具入口+登记边界名实测）、r9s_probe_f.py（组合面精查：
  wrapper×载体/位参语义/sort /O 方言）、r9s_probe_g.py（**新旧代际对照**，old=git 1889ba6）、
  r9s_probe_h.py（tee 多目标/copy /Y/.exe 两代际/PS 位参修法可行性 token 级视图）。
- 基线复跑（独立实跑，非转述）：test_handler ALL PASS 29+4+277；_verify_r9 46/0、r8 30/0、
  r7 30/0、r5 28/0、r3 25/0——与 round9-context 验收基线一致。

## 一、S-1~S-5 修复复测结论

| 项 | 攻击形复测 | 误拦负例复测 | 判定 |
|---|---|---|---|
| S-1 | `-o/-O` 粘连×反斜杠/大写/整词引号/cd 相对/内嵌一层/execute_code 链 全 block | `-O URL`、`-oL`、门外 grep/未知命令、门内非保护值、`ssh -oK=V`、`mount -o rem,rw`、`tar -O` 全 PASS | ✅修复成立（FP 面无伤） |
| S-2 | Copy-Item/Tee-Object 载体/裸位参/-Destination 形 全 block | **源位（备份读）由 PASS→block 新 FP**——见 F-9-1 | ⚠️修复方向引入误拦 |
| S-3 | `echo x & cp GUARD`、`>NUL &`、`&`×S-1/S-4/S-5 交叉、无空格 `hi&sudo` 全 approve | `2>&1 > ws`、`2>&1 \| findstr`、双引号/单引号 URL `a&b`、`set A=1&2&3`、文件名含 &、`&>`、`>&2`、&&/\|\| 混排 全 PASS；残段 `2>&1>CFG`/`>CFG&dir`/`&>CFG` 仍 block（"未登记残段边界"声明名实相符） | ✅修复成立，双向无伤 |
| S-4 | runas/sudo/time/env/nohup/LANG=C 前缀×cp/install/tee/sed -i/truncate/-o 粘连 全拦向正确；`env -i sudo -n time` 叠罗汉 approve | `env \| grep`、`time ls`、`sudo cat` 读、`nohup python &`、`sudo rm`、`runas …whoami`、workspace 正常写 全 PASS；cw 观测剔除链正常词零污染（`/usr/bin/cp` 错位族两代同向，附录③） | ✅修复成立 |
| S-5 | cmd/c 裸形、/q /c 多开关、pwsh -Command 裸、sh/bash/zsh 裸、双载体、二层/三层深度门内 全命中；处置分流正确（裸形 cp 语义=approve 非 block） | `cmd /c dir`、`Get-Date`、`copy ws 非保护`、内嵌引号体源位 全 PASS；引号体既有 M-1 分支零回潮 | ✅修复成立 |

## 二、发现（全部实测复现；old/new=1889ba6/cbd6301 对照，probe g/h）

### F-9-1（MED·本轮修复引入的纳入范围误拦）S-2 cmdlet 入「路径出现即写」分支，源位复制误拦
- 复现：`Copy-Item CFG 备份路径` old=**PASS** new=**block**；内嵌引号体形同陷；
  `-Container CFG -Destination ws`（CFG 在源位）block。对照 `cp CFG BAK` 两代 PASS。
- 判据：纳入范围误拦（boundary §纳入7 只义务"写目标是受保护路径"；round9-context 红线
  「改名/复制不拦」；与 cp 同语义处置分叉）。根因：_PS_WRITE_RE 分支（L711）为
  Set-Content 族设计"受保护路径出现在其之后即写"，无位参语义；Copy-Item/Tee-Object 是
  复制语义（首参/`-Path`=源），整词扩表即把源位读判成写。fix-009-input"按现口径不扩位参"
  的裁量对 Set-Content 族成立、对复制族 cmdlet 不成立——该 FP 面 TC-R9 未覆盖（探针实测才暴露）。
- 修法方向：Copy-Item/Tee-Object 自「出现即写」支摘出，走 `_COPY_CMDS` 同款末位/命名目标
  判定（cmd 位序 token 视图 probe h 实证可及），Set-Content/Add-Content/Out-File 保持现支。
  ≤6 行、零新解析层。

### F-9-2（MED·纳入范围新旁路）wrapper × 载体前导组合面未打通
- 复现（两代同陷，非回潮）：`sudo bash -c "cp evil <GUARD>"` → **PASS**；
  `sudo cmd /c "copy evil CFG"`、`sudo cmd /c copy evil CFG`（裸形）、`nohup/time bash -c "…"`、
  `time bash -c "echo x > CFG"` → PASS。对照：单独 sudo（S-4 封）、单独载体（M-1/S-5 封）。
- 判据：§纳入5 逐字点名 `bash -c "…"` × §纳入1 常规 cp；`sudo bash -c "…"` 是人类常规组合，
  非冷知识。probe f 实测 `LANG=C pwsh -Command Copy-Item…` 反而 block（_PS_WRITE_RE 巧合命中，
  通道未打通的伪装覆盖）——组合面正确性依赖巧合分支。
- 根因：`_EMBED_SHELL_RE`/`_BARE_CARRIER_RE` 均 `^\s*` 锚定裸载体词（probe f 名实测
  `regex 名实: sudo-prefixed=False`）；S-4 剔除链只喂 _command_word，不参与载体识别。
- 修法方向：M-1/S-5 匹配前对 seg 做一次既有剔除链的 wrapper 前缀剥离（复用 _command_word
  的剔除循环，≤6 行）；或两正则前缀放宽为可带 wrapper/赋值词首段。

### F-9-3（LOW·纳入范围新旁路）cmd 原生 `sort /O <file>` 输出位参方言零覆盖
- 复现（两代同陷）：`sort /O D:/…/config.yaml d.txt`、粘连 `/O` 形、`SORT /O`、
  `cmd /c sort /O …`、execute_code os.system 内同形 全 PASS；对照 `sort -o` 形已 block（S-1）。
- 判据：§纳入1 点名 sort 输出位参 + §纳入6"同语义必防"精神（Windows 部署面上 /O 是
  cmd 版 sort 唯一输出语法，非冷知识——man sort 一屏可见）。修法方向：_GLUED_O_RE 与
  _OUTPUT_FLAG_RE 门两处字符类 `^-` → `^[-/]`（≤6 行，灰区判据"5 行内可修"通过）；
  同 token 形 `/O` 与 S-4 选项剔除不冲突（cw('sort /O x d')='sort' 实测）。

### F-9-4（LOW·纳入范围新旁路）tee 多文件位参非末位漏拦
- 复现（两代同陷）：`echo x | tee evil.txt <CFG>`、`tee -a evil.txt <CFG>` → PASS；
  对照 `tee <CFG> out2.txt`（末位 CFG）→ block（首目标分支正确）。PS 别名 `tee evil CFG`
  内嵌形同陷（与登记"别名 tee 不修"不同根——此乃位参矩阵缺陷非词表缺陷）。
- 判据：§纳入1 点名 tee；POSIX tee 全部位参均为写目标，末位限定半覆盖=名实不符面
  （代码注释"tee 目标→写"未声明仅首位）。修法方向：prev=='tee' 判据改"段命令词==tee"
  （_command_word 现成，≤2 行）。

## 三、红线保持核查（全部实测）

1. **gateway restart block** ✅：restart/run/start、大写、bs+LF/bs+CRLF 续行、`hermes -p dev`
   全局 flag、**新交叉形**（`sudo hermes gateway restart`、`cmd /c` 裸形、`echo x & hermes
   gateway restart` 经 S-3/S-4/S-5 改动后）全 block；status/stop 不误伤 PASS。
2. **rm -r 平台层分层** ✅：`rm -r/rm -rf/sudo rm -rf/rd /s /q` 守卫目录全 PASS（插件不扩，
   与 CHANGELOG L71-72 分层登记一致；拦截职责在平台 approvals 层，config.yaml L205 实存）。
3. **cp 写配置弹卡** ✅：直写/引号/`copy /Y`/载体裸形（S-5 分流 approve 非 block 正确）/
   多 wrapper 叠加 全 approve；cp 源位备份 PASS；`mv` 改名族 PASS；非 cp 写配置
   （echo>/`2>`/sed -i）block；write_file/patch 守卫路径 block、workspace 负例 PASS。
4. approvals.mode manual、git push --force 永不白名单：插件不涉（框架层），未动 ✅。

## 四、附录：排除范围/登记边界实测罗列（一律不立项）

1. `sudo -u root cp …GUARD` → PASS：fix-009 §4 登记边界，实测维持（cw='root' 名实相符）。
2. wrapper 白名单面：`env -u VAR cp`、`nice -n 5 cp`、`xargs cp` → PASS——S-4 规格定死
   sudo|time|env|nohup|runas，禁扩范围红线，不立项。
3. 全路径/.exe 命令词族：`cp.exe`、`/usr/bin/cp`、`D:\tools\cp.exe` 写守卫 → 两代同向 PASS
   （S-4 剔除令 /前缀词错位但方向不变差；sed.exe/curl.exe 经 \b 分支照常命中 block）——
   r8 探针 b 已测未立项，前案维持。
4. `curl --output<粘连无=>` → PASS：POSIX curl 不接受该形（需 =/空格），非可运行命令，无防护语义；
   `-o=out…` 值首 = 形 PASS 方向正确（=前缀文件名非绝对路径）。
5. PS 别名 cp/tee 词表：登记不修维持；`pwsh -Command "cp …CFG"` 仍经 shell 链 approve（_verify_r9 双锁复跑 ok）。
6. `2>&1` 裂段内部形态（`type f 2>&1 > ws` → ['type f 2>','1 > ws']）：无 FP、无新漏（残段
   独立判定成立），族内观察项不立项。
7. verbatim 引号内形 `cp evil "\\?\D:\…CFG"` → approve：保守方向（fail-closed），排除§2 族。
8. robocopy/tar/ln 专属语义、跨家 tilde、会话级 cd 漂移（M-3）、变量间接/eval/编码混淆：
   既有登记，实测方向与登记一致（probe e NA 组）。
9. 三层 `bash -c "…'bash -c …'…"` 载体套嵌：depth+1 命中 approve（_NEST_DEPTH_LIMIT=3 门内，
   §纳入5"一层"义务满足；更深嵌套属排除§3 多解释器族）。

## 五、名实核查

- fix-009.md / CHANGELOG round9 节全部声明逐条实测相符（含"S-3 残段不登记"“别名 cp 仍命中”
  “_GLUED_O_RE 双 dash 天然不匹”等）；handler 新增行 ≤120 合规；**未发现名实不符立项**。
- 唯一名实微疵（不立项）：F-9-4 根因处的注释"tee 目标→写"实为"tee 首位目标→写"（文档口径，
  并入 F-9-4 修复顺手改注释即可，不独立成项）。

## 六、裁决

**CHANGES REQUIRED** —— 4 条：**F-9-1（MED，本轮引入误拦）**Copy-Item/Tee-Object 源位复制
误拦（纳入§7 反例×红线"复制不拦"×与 cp 同语义分叉）；**F-9-2（MED）**wrapper×载体前导组合
旁路（sudo bash -c "cp 守卫"实测 PASS，§纳入5×§纳入1 组合面）；**F-9-3（LOW）**cmd `sort /O`
输出位参方言漏拦；**F-9-4（LOW）**tee 多文件非末位目标漏拦。修法均 ≤6 行、零新解析层、复用
既有剔除链/矩阵分支，灰区判据通过。S-1/S-3/S-4/S-5 修复工程质量验收通过（双向复测零回潮）；
三条红线全保持；基线 29+4+277 / 46+30+30+28+25 独立复跑全绿；附录 9 族登记不立项。

—— sa-0（安全路）2026-09-22 round9 终审，全程只读；探针 r9s_probe_a~h.py（g 含新旧代际
对照 old=git 1889ba6）。
