# fix-009 修复规格（round9：安全路终审 S-1~S-5 + 质量路 N1 补锁向）

基线：git be14c7f（round8 + 质量路 NOTES 处置），250 用例 ALL PASS。
最高准绳不变：requirements/requirement-20260922-boundary.md（范围决策）。
本批 5 条 finding 均为安全路终审**实测复现**的纳入范围旁路（PM 已独立复验，
探针 reviews/fix009-scratch/pm_verify_009.py 输出为准），修法均已定死为
"≤6 行/零新解析层"，**禁止扩范围、禁止顺手重构、禁止新增解析状态机**。

## 改动清单（handler.py）

### S-1（HIGH）`-o<file>`/`-O<file>` 粘连提取
- 现状（PM 实测）：`curl -oD:/…/config.yaml http://x`、`curl -sSL -oD:/…/handler.py`、
  `sort -oD:/…/config.yaml d.txt` 全 PASS；对照 `curl -o <空格>路径` approve。
- 修法：仿 `_GLUED_T_RE` 增加输出标志粘连提取——token 匹配 `^-[oO](?![a-zA-Z0-9])`?
  不对：粘连形即 `^-o` / `^-O` 开头且长度>2、且第 3 字符不是 `=`——取 `-o` 后值
  进路径归一+判定（before 段认该选项词）。注意 `-sSL` cluster 不含 o/O 不受影响；
  `--output` 长形已有分支不得动。具体正则形态由实现者定，行为以验收 TC 为准。
- 误拦红线：`curl -O http://x/a.txt`（URL 后续段）现状行为不得回退；
  纯 `-output` 之类词不得当粘连（值以字母开头且是已知长选项前缀时保守放行与否
  按现有 -t 族同款口径处理——与 _GLUED_T_RE 的排除逻辑保持一致）。

### S-2（MED）PS cmdlet 词表扩集
- 现状：`pwsh -Command "Copy-Item evil D:/…/config.yaml"` 与
  `"Tee-Object -FilePath …"` PASS；对照 Set-Content approve。
- 修法：`_PS_WRITE_RE`（L252）词表扩 Copy-Item|Tee-Object（含别名 cp/tee?——
  **不含**，别名歧义大，登记不修）。1 行正则。

### S-3（MED）cmd 单 `&` 链式分段
- 现状：`echo x & cp evil <GD>` PASS；`&&` 形 approve。
- 修法：_judge_terminal L805 分段集 `("&&","||",";","\n","\r")` → 追加 `&`
  （_split_shell 按分隔符长度降序消费，&&/|| 先于单 & 已保证）。
- **FP/漏拦双向 TC 必测**（这是本批风险最高项）：
  - 不误拦：`type f 2>&1 > <workspace路径>`（无保护词）、`cmd 2>&1 | findstr x`；
  - 不新漏：`cmd 2>&1 > <GUARD文件>`（`>&` 裂段后残段 `>`+路径 仍须 block——
    重定向分支独立识别）；若做不到不扩，登记该残段形为接受边界并在 CHANGELOG 写明。
  - `curl "https://x?a=1&b=2"`（引号内 & 不得分段——_split_shell 若引号感知则天然安全，
    实现者必须先实测确认）。

### S-4（MED）前导 wrapper 词剔除
- 现状：`runas /user:admin cp evil <GD>`、`sudo cp …`、`LANG=C cp …` 全 PASS；裸 `cp evil <GD>` approve。
- 修法：`_command_word` 提取时循环剔除：`sudo|time|env|nohup|runas` 词 +
  `/xxx` 或 `-xxx` 选项词（仅在剔除 wrapper 后连续跳过）+ `^[A-Za-z_]\w*=` 环境赋值形，
  取下一个实词作为命令词。不改矩阵其他逻辑。
- 负例：`env | grep config` 放行不回退；`time ls` 放行。

### S-5（MED）载体裸形剥词递归
- 现状：`cmd /c copy evil D:/…/config.yaml`、`cmd /q /c copy …`、
  `pwsh -Command Copy-Item evil …` 全 PASS；同载荷引号体形 approve。
- 修法：载体词（cmd|cmd.exe|powershell|pwsh|sh|bash）命中且无引号体时，
  剥掉载体词与开关（`/c` `/k` `-c` `-Command` `-lc` 及其前置开关位），
  剩余文本以 depth+1 递归 _judge_terminal（受 _NEST_DEPTH_LIMIT 门）。
  ≤5 行，复用现有递归。
- 负例：`cmd /c dir <workspace>` 放行；`pwsh -Command Get-Date` 放行；
  引号体路径（_EMBED_SHELL_RE）既有分支不得回归。

## 质量路 N1 补锁向（test_handler.py，同批）
- TC 锁 `cp -"t"GUARD…` 半混劈 token tdir= 变体 PASS 方向；
- TC 锁 F-7-3 保守弹卡 `cp '-t' CFG out/` approve 方向。
（登记句已在 be14c7f 修正为"暂无 TC 场景"，补锁向后把该句改回"有锁"。）

## 过程与制品纪律（红线，违反=返工）
1. **先建 reviews/fix-009.md 骨架**（六节：0 行为映射/1~5 各 S 落地记录/6 验收），
   每完成一步立即追加落盘 + `[DONE S-x]` 标记。任何时刻中断，接续者可从
   文件判断进度。禁止攒到最后一次写。
2. 改动脚本先 compile 验证再落盘（原子纪律）；锚点必须先 grep 现场确认，
   禁止凭规格文本盲搜。
3. 新增 TC-R9 块：每条 S-x ≥1 封堵锁 + ≥1 误拦负例；S-3 双向必测形全覆盖。
4. 新建 _verify_r9.py（同场景集+回归负例：cat 读守卫、workspace 写、
   单引号路径、`curl -o 空格` 形、2>&1 族、`"a&b"` URL）。
5. CHANGELOG 追加 round9 节（含 S-3 若登记残段边界的明文）。
6. 验收四连（全部实跑贴末行）：`python test_handler.py`、`python _verify_r9.py`、
   `python _verify_r8.py`、`python reviews/fix009-scratch/pm_verify_009.py`
   （末项预期：S-1~S-5 的 PASS 行全部转 approve/正确方向，NEG 行不变）。
   再加 `python _verify_r7.py`、`_verify_r5.py`、`_verify_r3.py` 无回潮。
7. **不要 git commit、不要 deploy**（PM 门禁后统一做）。
8. 终答 ≤400 字：验收命令末行原文 + 改动文件清单 + S-3 残段处置结论。
