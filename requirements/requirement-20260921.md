# write-guard 插件增量需求 — 2026-09-21 决策集（REQ-20260921）

| 项 | 值 |
|---|---|
| 文档阶段 | REQUIREMENT（增量，追加于 requirement.md v1.1 与 requirement-c1.md 之后） |
| 日期 | 2026-09-21 |
| 范围 | 承载 2026-09-21 全部用户决策对 write-guard 的需求级变更；与 v1.1 冲突处**以本文为准** |
| 上游依据 | 用户 2026-09-21 各时点原话（见 FR-D 节逐条引用）；两轮独立对抗走查（deleg_fdfaf47f / deleg_b5774fc6）确认的绕过路径事实 |
| 历史文档 | requirement.md v1.1 与 design/design.md 为 2026-09-17 时点快照（reviews/review-001/002 引用其编号，不回改正文）；本文 + CHANGELOG 为现行权威 |

---

## 1. 决策原文（需求溯源）

| # | 用户原话 | 需求化 |
|---|---|---|
| U-1 | "对文件编辑工具, 如果路径里有这个目录下的配置文件, 直接拦截! 不要用户审批! 直接完全截断这种操作! 不允许直接编辑配置, 返回的提示说明必须按照skill流程操作, 不允许直接编辑配置文件" | FR-A1 |
| U-2 | "范围要扩大" | FR-A2 |
| U-3 | "cp要弹审批, cp是改配置文件的方法, 其他的方法总结阻断" | FR-A3 |
| U-4 | "改名和复制不拦截" | FR-A4（复制=cp 类维持 U-3 弹审批；改名/移动放行） |
| U-5 | "禁止使用 hermes gateway restart/run/start …加到插件中"；命中返回原话文案 | FR-D1 |
| U-6 | "读取工具就那么几个, 只写几个就行了 不要写太多! 其余的一律走参数检查!" | 已由 requirement-c1.md 承载（5 项清单），本文维持 |
| U-7 | "不能改源码" | CON-D1（实现约束） |

## 2. 功能需求（对 v1.1 的修订）

**FR-A1 文件编辑工具直接截断**（修订 FR-01~06 的处置动作）
- `write_file` / `patch` 的目标路径归一化后命中受保护配置 → `action=block`（不再 approve 弹审批）。
- block 消息三要素：工具名 + 目标路径（变体命中双段展示）+ 固定指引"必须按照 skill 流程操作（safe-config-modify），不允许直接编辑配置文件"。
- 平台语义依据：pre_tool_call 返回 block → 工具不执行、消息回传模型（模型停手报告，不得换方式重试）。

**FR-A2 受保护范围扩大**（修订 FR-02 判定口径）
- 受保护 = HERMES_HOME 前缀内 且（扩展名 ∈ {yaml, yml, json} 或 文件名含 "config" 或 .env 系列）。
- 非配置形态（skills/*.md、plugins/*.py、logs/、cache/ 等）不受保护。
- HERMES_HOME 目录本身（无文件叶子）不算受保护目标。

**FR-A3 terminal / execute_code 写配置分流处置**（修订 FR-03/FR-04/FR-10 处置动作）
- 复制类写目标（terminal: cp/copy/install；execute_code: shutil.copy/copyfile/copy2 目标位）→ `action=approve` 弹审批（保留人工通道，rule_key 按归一化路径）。
- 其余一切写形态（重定向 > / >>、tee、sed -i / perl -pi、dd of=、curl/wget/sort 输出参数含 = 粘连、open('w'/'a'/'x')、Path.write_text/write_bytes/touch、os.open 写标志、代码内 write_file/patch 调用、内嵌脚本）→ `action=block`。
- 无法静态判定读写方向 → 放行（Q-03 低误拦优先，继承 v1.1）。

**FR-A4 路径级操作放行**（继承 v1.1 OOS-09 并显式化）
- 改名/移动（terminal mv/ren；execute_code shutil.move/os.rename/os.replace）即使目标为受保护配置 → 放行。用户决策原话锁定，测试 TC-A-64/65/66 双向回归。

**FR-D1 Gateway 生命周期命令禁令**（新增守卫 D）
- `terminal.command` / `execute_code.code` 文本命中 `hermes (…全局 flag…) gateway (restart|run|start)`（忽略大小写，覆盖反斜杠续行、组合段内嵌）→ `action=block`。
- block 消息为**固定文案（用户指定原文，不做插值）**："你违反了用户的规则, 必须使用skill指定的方式来访问hermes gateway"
- 边界（有意决策，见 CHANGELOG 守卫 D 节）：`status` 放行；`stop` 不在禁令清单；按文本匹配（提及即拦）——嵌套执行面优先于误拦成本。
- 定位：防呆层（防错不防恶意），变量拼接/编码混淆声明为接受边界。

## 3. 约束与设计决策

- **CON-D1**：全部改动仅落于 write-guard 插件（handler.py / test_handler.py / deploy.py / 文档），**不修改 Hermes 框架源码**（用户红线）。
- **DR-D2**：守卫轮询顺序修订为 **[D, C, A, B]**（修订 v1.1 Q-01 的 [C,A,B]）：D 为最轻量精确正则置最前；C 仍先于 A/B，保持"任何守卫异常/改动不得旁路临时目录拦截"的结构性不变量（FR-14 继承）。
- **DR-D3**：守卫 D 独立函数、独立常量，与 A/B/C 零共享（CON-02 独立性原则延伸）。
- 质量决策（sa-1 审查后、按用户"最优设计自行决策"授权）：
  - 修订史外迁 `reviews/CHANGELOG-20260921.md`，代码注释只留设计理由（S-1）。
  - 测试桩按 `__name__` 定位（`_stub_guard`），禁止 GUARDS 硬索引（T-3）。
  - 清单"安全不变量"与"快照提醒"分断言（T-4）。
  - deploy.py 传输完整性 = 复制前源哈希 vs 部署后哈希（消除自指校验，R-7）。
  - 判定热路径正则全部预编译（R-8）。

## 4. 验收标准（增量）

| # | 标准 | 对应测试 |
|---|---|---|
| AC-D1 | write_file/patch 写受保护配置 → block，消息含工具名/路径/skill 指引 | TC-A-01~04、TC-M-01~03 |
| AC-D2 | profile.yaml / settings.yaml / .env / *.json 受保护；skills/*.md 放行 | TC-A-59~63 |
| AC-D3 | cp 类写配置 approve 弹卡；其他写形态 block | TC-A-17~33、TC-A-46~55 |
| AC-D4 | move/rename/replace 覆盖配置 → 放行 | TC-A-64~66 |
| AC-D5 | hermes gateway restart/run/start（含 flag/路径/大小写/续行/内嵌形态）→ block 且消息逐字等于固定文案；status/stop → 放行 | TC-D-01~14 |
| AC-D6 | 绕过路径封堵：~ 展开、MSYS /d/ 与 /cygdrive/d/、\\\\?\\ verbatim、单反斜杠转义保真 | TC-A-56~58、TC-A-62 |
| AC-D7 | 任一守卫异常不旁路 D/C（fail-closed 面）且不使插件整体失效 | TC-E-01~05 |
| AC-D8 | 判定行为与 S-1 注释手术前 AST 等价（去 docstring 后逐字节一致） | 手术时校验（一次性门禁，已执行） |
| AC-D9 | 全量测试 ALL PASS；部署一致；无源码修改（git status 干净） | 每轮复审必查 |
