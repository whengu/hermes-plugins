# fix-008 输入：round7 复审 findings 修复规格（PM 验证背书，2026-09-22）

基线 git 90de321（handler.py 现 1112 行）。执行者=修复 subagent；**只改
D:\myagent\workspace\write-guard\ 下 handler.py / test_handler.py，并写
reviews/fix-008.md 修复报告段。禁止：deploy、git 写操作、改 reviews/audit-round6-sec/
与 audit-round7-*/（复审侧脚本）、动主部署目录。**

## 红线（违反=整批作废）
- rm -r / 递归删除保持拦截；gateway 命令禁令保持 block；approvals 语义不动。
- 改名(mv/ren)/复制读向不拦；cp 写配置=approve 弹卡（不是 block）；其余配置写=block。
- **不加复杂度**：能改既有正则/分支就不新增结构；不引入 AST 解析级方案。
- 载荷纪律：任何含攻击字面量的验证必须写进 .py 文件执行（命令行零载荷），
  临时脚本只写 reviews/fix008-scratch/。

## Finding 1（HIGH）F-7-1 续行归一预处理有缺陷 —— 根因已由 PM 实测修正
现状 handler.py L751：`command.replace("\\\\\n"," ").replace("\\\\\r\n"," ")`
（值语义=把「反斜杠+换行」替换成「反斜杠+空格」，换行消失、反斜杠保留）。
PM 复测证明这个实现两头都不对：
1. **真续行旁路**：`cp evil \`+LF+`<GUARD>`（round6 D 卷对照形，shell 语义
   =一行命令 `cp evil <GUARD>`）→ 现状归一后成 `cp evil \<GUARD>`，
   `_split_shell` 引号外 `\x` 规则又吃掉反斜杠 → token=`GUARD无斜杠`… 实测
   **PASS**（应 approve）——即合法续行攻击面从未封住（CHANGELOG「D卷全9形
   封堵」失实，必须改口径）。
2. 盲替换不感知引号状态：`echo a\`+LF+`` ` ``cp evil <GUARD>`` ` `` 等带引号
   混排形（sa-1 F-7-1 backtick 形）→ 归一后整体成单 token → **PASS**。
   （注：`\`+LF+反引号 按 POSIX 不在双引号内，反斜杠转义的是反引号，sa-1 的
   "引号内不粘连"修法理由方向有误，以本 PM 实测根因为准。）

**要求修法（引号感知粘连，替代盲替换）**：在 _judge_terminal 入口用一个
引号状态机扫描（可复用 _split_shell 的状态思路）：
- **引号外** `\`+LF（含 `\`+CR+LF）=续行 → 删除这两个字符（行直接相接，
  不留空格——shell line-continuation 语义就是拼接，`cp evil \`LF+GUARD` 接出
  `cp evil D:/...` 中间空格来自行尾前的原有空白；若原串 `\` 前无空格相接处
  会并词，属 shell 同语义，可接受）；
- **双引号内** `\`+换行：bash 行为=删两者（行拼接，引号保持）→ 同删除；
- **单引号内**：字面保留（不做任何处理）；
- 反斜杠自身被转义（`\\` 成对）不作用于后随换行——逐字符状态机自然处理。
删除盲 replace 两行，改为该归一。归一后的既有分段（\n/\r 已在分段集）不动。

**必须新增 TC（test_handler.py run_r8_fixes）**：
- `cp evil \`LF+GUARD → approve（真续行，现状漏=核心回归点）
- `cp evil \`CRLF+GUARD → approve
- echo 双引号串内 `\`LF 拼接后含 GUARD 词 → 命中（按拼接语义）
- 单引号含 `\`LF → 不误伤（负例 PASS）
- `\\`+LF（转义反斜杠+换行）→ 换行仍分段（负例：`echo a\\`LF+`cp evil GUARD` → approve）
- 既有 TC-R7-01~14 全部保持绿。

## Finding 2（MED）F-7-2 引号粘连长形 `cp '--target-directory'=<dir>`
PM 实测 PASS（单双引号两形）。Q-6-1 收了裸粘连 `--target-directory=` 与
引号分离形，组合漏。修法（最小）：norm_raw 提取链加一腿——raw 以引号起始且
`_COPY_T_QUOTED_RE` 命中选项名、引号后紧跟 `=` → 取 `=` 后为路径（token 级
等价于 shell 剥引号后 `--target-directory=<dir>`… 实为两 token，但保守收集
进矩阵无害，判定仍由 -t 分支门把关）。-t 分支加同款识别（判 raw 前缀形）。
TC：`cp '--target-directory'=`+GUARD+` x` → approve；双引号形同；
负例 `cp '-t' workspace子路径 x`（非 home）仍放行。
F-7-3（LOW）`cp '-t' <CFG> out/`（'-t' 当文件名）假阳性弹卡——**登记边界**
（CHANGELOG 一句，方向保守），不修。

## Finding 2b（MED，sa-0 J 卷实测，待其报告定级背书）引号在 cluster 内的粘连形
`cp -'t'GUARD evil`（引号夹在 - 与 t 间）→ **PASS**；`cp -"t"GUARD evil` → **PASS**；
`cp evil -'t'GUARD` → **PASS**；`install -'t'HOME x` → **PASS**。
（对照 `cp '-t'GUARD` 引号包整词形已 approve——缺口在引号包**单字母 t** 的粘连位。）
归一修法与 F-7-2 同一处落子：norm_raw 提取前对 token 做「引号剥离归一」
（剥 token 内成对单引号/双引号后重走 _GLUED_T_RE / startswith 链），
一次覆盖 F-7-2 与 2b 全家族；负例：`grep '-t' file` 非 cp 族门仍放行、
`cp '-t' workspace子路径 x` 非 home 放行。
TC 补：J1a/J1b/J4/J5 四形（两引号 × 两词序）。

## Finding 2c（补充，sa-0 I/H 卷 shell 真值背书）半混引号长形
`cp -"target-directory" GUARD evil`（dash 在引号外）shell 剥引号后与裸长形同义
=真旁路（sa-0 H2 实测守卫 PASS）；引号剥离归一后应被 _COPY_T_QUOTED_RE/长形链
命中。TC 补一形。

## Finding 1b（补充，sa-0 POSIX 真值实证）反斜杠奇偶族
15:02 卷实测（POSIX bash）：`\`+LF=粘连（marker absent）；`\\`+LF=字面反斜杠+
粘连；**`\\\`（3 个）+LF=粘连且留一个字面 `\`**（marker CREATED：两行并成
`true \ touch X` 语义）；4bs=拆分（转义反斜杠完整，换行独立分隔符）。
引号感知状态机必须按「成对消耗、奇数个最后单 \ 才粘连」实现；
TC 补：3bs+LF 对准 GUARD 形（粘连后 cp evil \GUARD… token 提取由 _split_shell
既有 `\\x` 规则处理，判定结果 approve/PASS 均可接受但**不允许整条旁路成
"两段各自无写语义"**——粘连必须在分段前发生）。

## Finding 3（LOW/OBS）F-7-4 长行与登记口径
- L525/L535（110~113 字符）：在 CHANGELOG 明文写行长阈值=**120**（工程现状
  口径），≤120 不处理；
- CHANGELOG round7 条目「D 卷全 9 形封堵/零回潮」**改为如实口径**：NL 分段
  修复了裸换行族，但 `\`+LF 续行归一存在实现缺陷（真续行曾旁路）→ round8 修复。
  **CHANGELOG 绝不允许与实效分叉**（历轮教训）。

## 验收（PM 门禁实测，缺一退回）
1. `python -m py_compile handler.py` 通过；
2. `python test_handler.py` → ALL PASS（29+4+233+新增 TC-R8 全过）；
3. `python _verify_r7.py` 28→30 全绿不回潮 + `python _verify_r8.py`
   （新建，PM 会复核其内容）F-7-1 两向/F-7-2 组合形全过；
4. reviews/fix-008.md 记录：设计说明、改动行清单、新增 TC 清单、口径修正说明；
5. 不得触碰 deploy.py/主部署/git。