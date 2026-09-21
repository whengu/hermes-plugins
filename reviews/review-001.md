# write-guard 扩展代码独立走查结论（CODE_REVIEW）

| 项 | 值 |
|---|---|
| 审查对象 | `D:\myagent\workspace\write-guard\handler.py`（601 行，扩展后）；`D:\myagent\workspace\write-guard\test_handler.py`（502 行，102 用例） |
| 审查角色 | 独立只读代码走查子智能体（不修改任何源文件；唯一写盘 = 本文件） |
| 审查日期 | 2026-09-17 |
| 权威依据 | requirement.md v1.1（已 PASS）；design.md v2.0（DR-01~27，DESIGN_FIX 已落实）；design/review.md（PASS）；requirements/review2.md（PASS） |
| **测试基线（实测）** | `python D:/myagent/workspace/write-guard/test_handler.py` → **退出码 0，输出 `ALL PASS (29 scan cases + 4 hook cases + 69 new cases)`**，全部用例通过 |
| **总体结论** | **打回（REVISE）**：HIGH=0、MED=2、LOW=6。2 条 MED 为必须修复项（1 条实现与设计不一致的识别分支失效，1 条可绕过受保护配置的写形态识别缺口）；修复后需复跑全部测试并复核 |

---

## 0. 走查方法与实证

- 逐条对照需求 FR-01~14 / NFR-01~05 / AC-01~10 / CON-01~06 与设计 DR-01~27，按 9 个维度独立核验；
- 对可疑形态全部以真实调用 `handler.on_pre_tool_call(...)` 实证（只读，无磁盘写入）；
- C 项迁移零改动：用 `git diff` 进程替换对比初始提交（e2ce1cd）的原始 `on_pre_tool_call` 函数体与当前 `_guard_tmpdir` 函数体——**主体逐行一致，仅函数名行与 docstring 变化**；模式组、工具映射、拦截消息文本、`_scan` 均与初始提交逐字节一致；
- 源码事实核实（DR-27 / DR-13 / FR-01 依据）：`file_tools_paths.py::_resolve_base_dir` 确认 write_file/patch 相对路径基准为 task workspace root、进程 cwd 兜底（注释声明属实）；`memory_tool.py` 注册名 `memory`（写工具）；`anthropic_adapter.py` OAuth 别名 `context_notes`；hindsight 插件注册名 `hindsight_retain`（写）/ `hindsight_recall` / `hindsight_reflect`（查）；HERMES_HOME 环境变量为 Hermes 真实使用的配置目录变量。B 项写集合 {hindsight_retain, memory, context_notes} 与源码事实吻合，未见其他写记忆工具遗漏。

---

## 1. 需求/设计符合性总核验（走查要点 1）

| 需求 | 实现对应 | 判定 |
|---|---|---|
| FR-01 受保护判定 + HERMES_HOME 运行时来源/空值回退 | `_hermes_home()` handler.py:319-323（每次实时读取、`or` 回退默认值、不缓存） | ✅（TC-A-40~42 实证） |
| FR-02 命中 approve + 四工具最低强制集 | `_CONFIG_SCAN_TOOLS` handler.py:97 + `_guard_hermes_config` 538-547 | ✅ 范围无收缩（识别缺口见 MED-2） |
| FR-03 读取放行 | 只读命令/读模式/输入重定向/路径级操作均放行 | ✅（TC-A-26~28/34/35/45） |
| FR-04 路径等价四类 | `_normalize_path` 七步（环境变量展开大小写不敏感+词边界 → 引号剥离 → 字符串转义解义 → 分隔符统一+压缩 → 相对段归一 → 绝对化 → 小写化），handler.py:276-316 | ✅（TC-A-06~18/43/44/47 实证） |
| FR-05 范围外放行 | `_is_protected_config` 前缀+文件名含 config 子串，handler.py:326-335 | ✅ |
| FR-06 A 消息含路径/原因/工具名 | `_CONFIG_APPROVE_TEMPLATE` + `_approve_result` 356-366（字面命中展示原文 DR-16；变体命中双段展示 DR-24） | ✅（TC-M-01~04/08） |
| FR-07 B 写工具 approve、范围=所有写记忆工具 | `_MEMORY_WRITE_TOOLS` handler.py:109-113，精确集合 {hindsight_retain, memory, context_notes}，已对照源码核实 | ✅（TC-B-01~03） |
| FR-08 查询放行 | 工具名不在写集合即放行 | ✅（TC-B-04~06） |
| FR-09 B 消息含工具名+原因 | `_MEMORY_APPROVE_TEMPLATE` | ✅（TC-M-05/06） |
| FR-10/FR-11 C 行为不变/逻辑不改 | git diff 实证逐行一致（见第 0 节） | ✅ |
| FR-12/FR-13 轮询 [C,A,B] 命中即返/无命中放行 | `GUARDS` handler.py:568-572 + `on_pre_tool_call` 575-601 | ✅（TC-S-01~03，含桩计数断言） |
| FR-14 异常隔离契约 | 项级 try/except + `logger.exception` + continue + 外层防御兜底，不依赖平台 hook 兜底 | ✅（TC-E-01~05，含日志捕获断言） |
| NFR-01 独立性 | 三守卫独立函数、判定数据隔离 | ✅ |
| NFR-02 可维护性 | 五分区结构、命名清晰、规则来源注释充分 | ✅（小问题见 LOW-6） |
| NFR-03 可测试性/只读 | 纯内存调用、环境变量保存恢复、os.getcwd monkeypatch、GUARDS 桩恢复 | ✅ |
| NFR-04 回归 | 29 scan + 4 hook 旧用例原样通过 | ✅ |
| NFR-05 性能 | 纯内存正则/字符串计算，无 IO/网络 | ✅ |
| AC-01~10 | 用例映射：AC-02→TC-A-01~04/19~25/30~33；AC-03→TC-A-06~18/43/44；AC-04→TC-A-26~28/34/45；AC-05→TC-B；AC-06→旧用例；AC-07→TC-S-03；AC-09→TC-S-01/02（桩）；AC-10→TC-E-01~05；AC-08 走查项见本文件 | ✅ 全覆盖 |
| CON-01~06 | 单一插件/独立函数/轮询调度/C 项不改/单 hook/流程约束 | ✅ |

**完整性结论：需求全量落地，无收缩、无遗漏；C 项零改动实证成立。问题集中在识别完备性（MED）与若干边界语义（LOW）。**

---

## 2. Findings 清单

### MED（2 条，必须修复，修复后复测）

**MED-1 — `os.open` 底层写标志识别分支恒失效（死代码），设计 DR-10 明示形态实际不拦截**
- 位置：handler.py `_judge_execute_code`（499-531 行），问题语句 521-524 行：
  ```python
  for m in _OS_OPEN_RE.finditer(code):
      content = _call_content(code, m.end() - 1) if m.end() <= len(code) and code[m.end() - 1] == "(" else ""
      if any(flag in content for flag in _OS_WRITE_FLAGS):
          record(m.start(), m.group(2), _normalize_path(m.group(2), base=base))
  ```
- 问题：`_OS_OPEN_RE` 匹配止于路径右引号（`\1\s*` 结束），`m.end() - 1` 恒为引号字符、恒不等于 `(`，因此 `content` 恒为空串、`any(...)` 恒为 False——该分支从不生效。`_call_content`（485-496 行）实际从未被有效调用。实测：`execute_code` 代码 `os.open(受保护配置文件路径, os.O_WRONLY)` → 返回 None（放行），而设计要求 DR-10 / 设计 3.2.3「底层打开写标志」形态必须拦截。
- 证据：设计 3.2.3 写方向形态清单第 4 行「底层打开写标志：`os.open(受保护路径, 标志)` 且标志含 O_WRONLY / O_RDWR / O_CREAT / O_APPEND / O_TRUNC（写标志形态，属设计细化扩充）」；DR-10 同述。实测输出见本文件第 0 节记录（os.open 写标志 → None；对照组 `open(路径,'w')` → approve 正常）。
- 附带缺口：test_handler.py 全部 102 用例**无 os.open 形态用例**（设计 7.2 用例清单亦未列），故该死代码未被任何测试暴露——与 MED-1 互为印证，测试充分性不足（走查要点 5）。
- 修复要求：
  1. 修正参数内容提取：改为从 `os.open(` 起始括号之后配对提取（如基于 `m.start()` 定位括号再 `_call_content`），确保写标志字符串参与判定；
  2. 补测试（至少两条）：`os.open(受保护路径, os.O_WRONLY)` → approve；`os.open(受保护路径, os.O_RDONLY)` → 放行（读标志负例）；
  3. 修复后实测该形态命中，复跑全部测试 ALL PASS。

**MED-2 — terminal 写形态矩阵遗漏「命令输出参数」类明确写形态（curl 的 -o / wget 的 -O 等），受保护配置存在可被利用的写绕过窗口**
- 位置：handler.py `_terminal_position_is_write`（408-437 行）与 `_judge_terminal_segment`（464-482 行）的写语义判定矩阵：仅覆盖输出重定向、输入重定向、`of=`、tee、sed/perl 原位编辑、复制类、移动类；未识别「带输出文件参数的命令」（如 `curl -o <路径>`、`wget -O <路径>`、`sort -o <路径>` 等）。
- 问题：`curl -o` / `wget -O` 的路径参数**语义明确是写目标**（输出文件），属 FR-02 ③「cp 至受保护目标、echo/tee/重定向写受保护文件等**明确写形态**」词面范围（「等」字授权扩展），并非 Q-03「无法可靠判定读写语义」的放行类；且下载写文件是语言模型生成命令的高频写形态。实测：`terminal` 命令 `curl -o D:\myagent\.hermes\config.yaml https://x.com` → None（放行）；`wget -O ...` → 同。对照：同命令改重定向形态（`curl ... > 受保护路径`）则被拦截——同义写操作因形态不同而漏拦，构成 A 项一致性缺口。
- 证据：FR-02 ③ 原文「（cp 至受保护目标、echo/tee/重定向写受保护文件等明确写形态；无法判定者默认放行）」；Q-03 放行仅限「无法可靠判定」者；OOS-03 排除的是「间接写、别名、动态构造路径等静态**无法可靠识别**的形态」——`curl -o` 属静态可明确识别。设计矩阵未列入（设计边界），但按用户「质量必须好、安全防线找漏洞」要求与 FR-02「等」字范围，应收敛处理。
- 修复要求（二选一，FIX 阶段执行其一并回填记录）：
  1. 实现补充：矩阵增加「命令输出参数」形态——识别已知带输出文件参数的写命令（至少 curl 的 -o/-O、wget 的 -O、sort 的 -o 等），受保护路径作为其输出参数时判写；未知命令含 -o/-O 形态按无法判定放行（保持低误拦）；
  2. 或提请用户/需求方显式确认该形态放行决策，按 Q-08 流程回填需求与设计文档声明边界；
  3. 无论走哪条路，补对应测试用例（拦截形态与放行形态各一），并复跑全部测试。

### LOW（6 条，建议修复，不阻断修复循环整体验收但列入修复清单）

**LOW-1 — terminal 管道内 cd 前缀贪婪匹配吞段，管道后真实写形态被跳过判定**
- 位置：handler.py 450-456 行 `_CD_PREFIX_RE = re.compile(r"^(?:cd|pushd)\s+(?:/d\s+)?(.+)$")` 的 `(.+)$` 贪婪匹配 + `_judge_terminal` 的分段逻辑（`re.split(r"\s*&&\s*|;", ...)` 不按管道切分）。
- 问题：`cd <目录> | <写命令>` 整段被当作 cd 段吞噬（目标含管道后全部文本），`continue` 后管道后的写形态不被判定。实测：`cd D:/myagent/.hermes | echo hi > config.yaml` → None（放行）。真实 shell 语义中管道左侧 cd 在子进程、不影响右侧写基准（写的是父进程 cwd 相对路径），故现实危害≈0；但与设计 3.2.2「管道两侧环境独立，不跨管道传播 cd」的判定意图不符——设计意图是管道两侧独立判定，实现却整体丢弃。
- 修复要求：`_CD_PREFIX_RE` 目标改为非贪婪并排除管道符（或先按管道分段、cd 段只在其所在段内生效、管道后各段独立判定）；补一条管道形态用例。

**LOW-2 — cd 目标「无法静态解析 → 放行」实现语义与设计不符（污染 cwd 继续判定而非立即放行）**
- 位置：handler.py 450-456 行（`_judge_terminal` 的 cd 分支）。
- 问题：设计 3.2.2 / DR-09 明确「cd 目标无法静态解析（变量、复杂嵌套）→ 按无法判定处理 → 放行（Q-03）」；实现中未定义/动态变量目标（如 `$VAR`）经展开保留原样后 `_normalize_path` 按相对路径**拼接进 cwd** 并继续判定后续段，而非立即返回 None 放行。归一化对非空字符串几乎不返回 None，故「无法解析即放行」分支实际不可达。行为结果大概率同为放行（污染 cwd 不命中受保护），但后续相对路径判定基于被污染的 cwd，存在判定基准不可信的误拦/漏拦不确定性（如 `cd $DEST && echo hi > config.yaml` 的写侧判定基于错误 cwd）。
- 修复要求：cd 段展开后仍含未解析引用标记（如残留美元符/百分号对）时按设计语义立即 return None（整条命令放行）；补一条动态 cd 目标用例断言放行且不污染后续判定。

**LOW-3 — write_file/patch 相对路径判定基准未随 DR-27 核实结果闭合（注释已核实、实现未校准）**
- 位置：handler.py 281-284 行注释（已如实核实真实基准为 task workspace root、进程 cwd 兜底，源码 `file_tools_paths.py` 属实）与 `_judge_path_param`（369-377 行，仍用 `os.getcwd()` 作基准）。
- 问题：DR-27 的核实义务文字为「核实后……仅影响相对路径形态的判定基准」——注释完成了核实陈述，但判定实现未采用核实结果。task 会话 cwd 与 Hermes 进程 cwd 不一致时（如 task 恰在受保护目录内工作），`write_file("config.yaml")` 真实写入受保护文件而守卫判定基准（进程 cwd）不命中 → 相对路径形态漏拦。风险面小（task cwd 默认即进程 cwd，相对路径写受保护目录场景罕见），但既已核实即应闭合。
- 修复要求：二选一——① 利用 hook 的 task_id 解析 task workspace root 作为基准（需确认无 IO/无副作用，满足 NFR-05）；② 显式在代码注释与设计第 12 节声明该落差为接受边界（进程 cwd 基准、Q-03 兜底）。

**LOW-4 — 测试硬编码用例计数 `_NEW_CASE_COUNT = 69`，与 `_rec` 调用次数弱耦合**
- 位置：test_handler.py 89 行。
- 问题：计数仅用于打印（ALL PASS 行），不参与断言；新增/删除用例后若不同步更新，输出仍显示旧数字（虚假声明），测试不会失败。当前 69 与实测一致（47 A + 6 B + 3 S + 5 E + 8 M），但属脆弱设计。
- 修复要求：改为 `_rec` 内部运行时自增计数（或删除该常量），使输出数字永远与实际断言数一致。

**LOW-5 — 设计 5.2「日志不包含系统临时目录字样」与 C 项原日志（含命中模式原文）自相矛盾**
- 位置：设计文档 5.2 节 vs 设计 2.1 节 / handler.py 166-168 行（C 项原样保留的 `logger.warning("... 命中模式 %r", ..., hit)`）。
- 问题：C 项原日志输出命中模式原文（设计 2.1 明确 C 项日志文案原样保留，FR-10/CON-04 更强约束），而设计 5.2 声称「日志不包含系统临时目录字面量，仅含守卫名、task_id、action」——两处表述冲突；测试运行输出中确实打印了命中模式原文。实现选择保留 C 原日志是正确的（FR-10 优先），但设计文档内部张力应澄清。
- 修复要求：设计 5.2 将该约束限定为「新增守卫（A/B）日志」；代码无需改动（C 项日志受 FR-10 保护）。

**LOW-6 — 环境变量展开为单轮非递归，HERMES_HOME 值本身含引用时保护基准漂移（防御纵深建议）**
- 位置：handler.py `_expand_env`（224-235 行）单轮替换。
- 问题：若运行时 HERMES_HOME 值本身含环境变量引用（如指向用户目录的引用形态），`_hermes_home()` 归一化结果与实际目录不一致 → 保护基准漂移（漏拦方向）。实际风险极低：HERMES_HOME 由 Hermes 进程设置，攻击者无法经工具调用修改 Hermes 进程环境变量（终端内赋值只影响子进程）；且当前实测环境 HERMES_HOME 为字面路径。属防御纵深建议。
- 修复要求（可选）：展开函数支持有限次递归（如 2 轮）或对 HERMES_HOME 值展开后再归一；不修则显式注释声明该假设。

---

## 3. 安全性专项结论（走查要点 3：攻击者视角）

| 攻击面 | 结论 |
|---|---|
| 轮询顺序/异常隔离旁路 C | 无漏洞：C 结构性最前 + 项级 try/except + continue，A/B 异常不可能旁路 C（TC-E-01/05 实证） |
| A 项前缀判定整体失效 | 无漏洞：统一正斜杠常量 `_SEP`，禁用 os.sep（MED-1 设计陷阱已落实），大小写/分隔符/转义/相对段等价类全覆盖（TC-A-06~18/43/44） |
| B 项写工具绕过 | 无漏洞：集合精确匹配 + 已对照源码核实全集；查询工具（recall/reflect）放行符合 FR-08 |
| approve 返回结构 | 合规：`{"action":"approve","message":...,"rule_key":...}`，无额外字段；rule_key 按归一化路径/工具名（DR-12/DR-14） |
| 无法判定默认放行 | 符合 Q-03 低误拦优先；放行形态均属设计接受边界（动态构造/间接写/别名） |
| **可绕过窗口（实证）** | ① `os.open` 写标志形态（MED-1，设计要求识别却失效）；② `curl -o` / `wget -O` 输出参数写形态（MED-2，静态明确写语义却放行）；③ 管道内 cd 吞段（LOW-1，现实危害≈0） |
| 误拦风险 | 文件名含 config 子串规则略宽（目录名含 config 时误拦，如 write_file 指向 config 命名目录）——R4 已声明，方向为 fail-closed，可接受 |

## 4. 质量专项结论（走查要点 8）

- 命名/职责：守卫函数独立清晰（CON-02），判定函数单一职责，常量集中注释来源充分；
- 无未用 import、无重复逻辑；`_call_content` 为 MED-1 引入但从未有效工作（与 MED-1 同修）；
- 异常处理：项级隔离 + 外层防御兜底，`logger.exception` 记录堆栈，日志前缀可检索；
- 日志分级：C 命中 WARNING（原样）、A/B 命中 INFO、跳过点 DEBUG、异常 exception——分级正确；
- 测试质量：消息内容断言（TC-M-01~08）、桩调用计数（TC-S-01/02）、日志捕获（TC-E-02/04）均为有力断言；组合断言（如 TC-A-05 多条 ok 合并）失败时可定位性一般，非阻断；**缺口：无 os.open 用例（与 MED-1 同修）、无 curl 输出参数用例（与 MED-2 同修）、无管道 cd 用例（与 LOW-1 同修）**。

---

## 5. 修复要求清单（供 FIX 阶段逐条处理）

1. **MED-1**：修复 `_judge_execute_code` 中 `os.open` 参数内容提取逻辑（定位起始括号配对），使写标志判定生效；补 os.open 写/读两条用例；实测命中 + 全量复测。
2. **MED-2**：terminal 写矩阵补充「命令输出参数」形态识别（curl -o/-O、wget -O、sort -o 等至少高频下载工具），或按 Q-08 流程提请用户显式确认放行并回填需求/设计；补拦截/放行各一条用例；全量复测。
3. **LOW-1**：cd 前缀正则排除管道符（或按管道分段独立判定），补管道形态用例。
4. **LOW-2**：cd 目标不可静态解析时按设计语义立即放行（return None），补动态 cd 目标用例。
5. **LOW-3**：write_file/patch 相对路径基准按 DR-27 核实结果闭合（用 task workspace root 或显式声明接受边界）。
6. **LOW-4**：测试用例计数改运行时自增。
7. **LOW-5**：设计 5.2 日志约束限定为 A/B 新增守卫（文档修订，代码不动）。
8. **LOW-6**：环境变量展开递归或显式声明假设（可选）。

**复测要求**：FIX 完成后重跑 `python D:/myagent/workspace/write-guard/test_handler.py`，退出码 0 + ALL PASS；并复核 MED-1/MED-2/LOW-1 三条实证命令转为拦截/放行预期后与实现一致。

---

### 走查统计

- 总体裁决：**打回（REVISE）**，进入 FIX 循环
- Findings：**HIGH=0、MED=2、LOW=6**（共 8 条）
- 需求覆盖：FR-01~14 / NFR-01~05 / AC-01~10 / CON-01~06 全部核验，无遗漏无收缩
- 测试基线：退出码 0，ALL PASS（29 scan + 4 hook + 69 new = 102 断言组）
