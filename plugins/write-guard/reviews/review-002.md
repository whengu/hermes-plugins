# write-guard 扩展 FIX 复审结论（CODE_REVIEW 第二轮 / review-002）

| 项 | 值 |
|---|---|
| 审查对象 | `D:\myagent\workspace\write-guard\handler.py`（661 行，FIX 后）；`D:\myagent\workspace\write-guard\test_handler.py`（545 行，110 断言组） |
| 审查角色 | 独立只读复审子智能体（不修改任何源文件；唯一写盘 = 本文件） |
| 审查日期 | 2026-09-17 |
| 权威依据 | review-001.md（8 条 findings + 修复要求清单）；requirement.md；design.md |
| **测试基线（实测）** | `python D:/myagent/workspace/write-guard/test_handler.py` → **退出码 0**，输出 **`ALL PASS (29 scan cases + 4 hook cases + 77 new cases)`**（合计 110 断言组），全部通过；77 与 `_rec` 运行时自增计数一致 |
| **总体结论** | **PASS**：8 条 findings 全部真实修复并经独立实证；无新引入的阻断性缺陷。遗留 5 条非阻断改进建议（其中 2 条为 MED-2 形态边界：1 漏拦 1 误拦，均罕见场景，见第 3 节） |

---

## 0. 复审方法与实证

- 只读复审：读取 FIX 后 handler.py / test_handler.py 全量源码，对照 review-001 的 8 条 findings 逐条核验；
- 关键形态全部以真实调用 `handler.on_pre_tool_call(...)` 独立复测（纯内存、无磁盘写），并额外设计测试套件之外的边界用例（写标志全集、组合标志、路径含括号、`-o` 引号粘连、echo 参数含命令名、引号内管道、已定义/未定义变量 cd、自引用环境变量等）；
- C 项迁移零改动用 `git diff`（初始提交 e2ce1cd 的 `on_pre_tool_call` vs 当前 `_guard_tmpdir`）逐行比对：**差异仅 3 处——函数签名行（更名 + 返回类型注解）、docstring、EOF 空行，函数体逐行一致**，C 项零改动成立；
- 新增用例与原有用例的 `_rec` 调用数人工清点：TC-A-01~55（55）+ TC-B-01~06（6）+ TC-S-01~03（3）+ TC-E-01~05（5）+ TC-M-01~08（8）= **77**，与运行时输出 77 一致（LOW-4 修复生效）。

---

## 1. findings 逐条核验

### MED-1（os.open 写标志分支）— **已修复 ✅**

- **修复方式**（handler.py 574-584 行）：弃用原 `m.end()-1`（恒为引号、恒不等于 `(`）的错误定位，改为 `open_paren = code.find("(", m.start())` 定位调用左括号，再经 `_call_content`（538-549 行）括号配对提取参数内容，`any(flag in content ...)` 判定写标志；
- **证据（独立复测，execute_code 形态）**：
  - `os.open(<受保护路径>, os.O_WRONLY / O_CREAT / O_APPEND / O_RDWR / O_TRUNC)` → 全部 approve ✅（写标志全集识别）
  - `os.open(<路径>, os.O_RDONLY)`、`os.open(<路径>, os.O_RDONLY | os.O_BINARY)` → 放行 ✅（读标志负例）
  - `os.open(<路径>, os.O_WRONLY | os.O_CREAT)` 组合标志 → approve ✅
  - `os.open(<路径>)` 无标志 → 放行 ✅
  - `x = os.open (<路径>, os.O_WRONLY)` 前导空白 → approve ✅
  - 路径含括号 `os.open('...config(1).yaml', os.O_WRONLY)` → approve（写语义正确拦截，fail-closed 方向）；同路径 O_RDONLY → 放行 ✅
- **边界分析**：`code.find("(", m.start())` 从 `os.open` 起点向后找第一个 `(`——`os.open` 与调用左括号之间仅有 `\s*` 空白，不可能插入其他 `(`，故定位必为调用括号（路径内括号必然出现在调用括号之后，不受影响），修复稳健；
- **测试**：TC-A-50（写标志 approve）、TC-A-51（只读负例放行）通过，补测要求满足。

### MED-2（terminal 命令输出参数形态）— **已修复 ✅（核心形态），遗留 2 个罕见形态边界（见第 3 节建议-1/建议-2）**

- **修复方式**（handler.py 404-411、452-457、519-526 行）：新增 `_OUTPUT_FLAG_CMDS_RE`（curl/wget/sort）+ `_OUTPUT_FLAG_RE`（before 以 `-o/-O/--output/--output-document` 结尾）+ `_OUTPUT_FLAG_EQ_RE`（`=` 粘连形态，token 级提取真实路径）；判定要求 before 文本含已知命令名 **且** 以输出标志结尾 → 判写；未知命令含 `-o` 不在命令集 → 放行（低误拦 Q-03）；
- **证据（独立复测）**：
  - 识别命中：`curl -o`、`curl -O`、`wget -O`、`wget --output-document`、`sort -o`、`curl --output=`、`curl -o=`、`curl --output`（空格分隔）、`curl -o`（URL 之后）、多 `-o` 第二目标、`curl --output="..."`（引号内 = 粘连）、相对路径 `curl -o config.yaml`（cwd 在受保护目录）→ 全部 approve ✅
  - 放行负例：`curl -o <非受保护路径>`、`curl -o <URL>`（不把 URL 当路径误拦）、未知命令 `custom_tool -o <受保护路径>`、`grep -o 'x' <受保护路径>`（grep 不在命令集）→ 全部放行 ✅
  - 既有形态回归：`echo hi | tee <受保护路径>` 仍 approve ✅
- **测试**：TC-A-52~55 四组（拦截、非受保护负例、wget/sort/--output= 组合、未知命令低误拦）通过，修复要求 1 补测满足。

### LOW-1（管道分段 cd 吞段）— **已修复 ✅**

- **修复方式**（handler.py 397-400、474-507 行）：双保险——① `_CD_PREFIX_RE` 目标改为 `([^|]+)$` 排除管道符；② `_judge_terminal` 先按 `\s*\|\s*` 管道分段，每段重置 `pipe_cwd = cwd`（管道两侧环境独立，cd 不跨管道传播），段内再按 `&&`/`;` 分段 + cd 链静态跟踪；
- **证据（独立复测）**：
  - `cd D:/myagent/.hermes | echo hi > config.yaml`（cwd=workspace）→ 放行 ✅（管道左侧 cd 不传播，写侧基于原 cwd 未命中）
  - `cd D:/other | echo hi > <受保护绝对路径>` → approve ✅（右段独立判定仍识别）
  - `echo hi > <受保护绝对路径> | cd D:/other` → approve ✅（左段写识别）
  - `cd D:/myagent/.hermes && echo hi > config.yaml`、`cd D:/myagent/.hermes; echo hi > config.yaml` → approve ✅（&& / ; 分段行为无回归）
  - `echo "a|b" && echo hi > <受保护绝对路径>` → approve ✅（引号内管道被拆分但写段仍独立判定命中，不产生漏拦）
- **测试**：TC-A-48（管道不吞段 + 两侧独立）通过。

### LOW-2（动态 cd 立即放行）— **已修复 ✅**

- **修复方式**（handler.py 494-502 行）：cd 段 `_expand_env(target)` 后仍含未解析引用（`_ENV_REF_RE` 命中残留 `$VAR`/`${VAR}`/`%VAR%`/`$env:VAR` 形态）→ 整条命令立即 `return None`，不再拼接 cwd 继续判定；
- **证据（独立复测）**：
  - `cd $WGUARD_UNSET_X && echo hi > <受保护绝对路径>`、`cd ${...}`、`cd %...%` → 全部立即放行 ✅（后续受保护写形态不判定，符合 Q-03）
  - 合法 cd 不误伤：`cd D:/myagent/.hermes && echo hi > config.yaml` → approve ✅
  - 已定义变量正常跟踪：设 `WGUARD_DEF=D:\myagent\.hermes` 后 `cd $WGUARD_DEF && echo hi > config.yaml` → approve ✅（展开后 cwd 正确更新并参与后续判定）
  - 边界：目录名含 `$` 字面（`cd D:/my$agent/x`）被当作未解析引用放行——fail-open 方向但属 Q-03「无法可靠判定 → 放行」接受语义，无安全影响（列入建议-4）；
- **测试**：TC-A-49 通过。

### LOW-3（write_file/patch 相对路径基准）— **已修复 ✅（走修复要求②：显式声明接受边界）**

- **修复方式**：`_normalize_path` 注释（285-291 行）与 `_judge_path_param` 注释（380-386 行）完整声明：① 已对照源码核实 Hermes 真实基准为 task workspace root、进程 cwd 兜底（`tools/file_tools_paths.py`，第一轮已核实）；② 守卫以进程 cwd 为判定基准，与 Hermes 兜底基准一致；③ task cwd 与进程 cwd 不一致时的理论漏拦为**显式声明的接受边界**，理由充分（task cwd 默认即进程 cwd、相对路径写受保护目录场景罕见、Q-03 低误拦优先、不在插件内复制 Hermes 内部路径解析以避免实现漂移与潜在 IO，保持 NFR-05 纯内存）；
- **判定**：声明准确、边界合理、与设计第 12 节「接受边界声明」要求一致；未引入 task workspace root 解析（符合修复要求②选项），代码零改动仅注释闭合——符合 review-001「二选一」的既定范围。

### LOW-4（用例计数硬编码）— **已修复 ✅**

- **修复方式**（test_handler.py 89、100-105 行）：删除常量 `_NEW_CASE_COUNT`，改 `_rec` 内 `global _new_case_count; _new_case_count += 1` 运行时自增，`ALL PASS` 打印使用运行时值；
- **证据**：实测输出 `ALL PASS (... + 77 new cases)`；人工清点全部 `_rec` 调用 = 77（55 A + 6 B + 3 S + 5 E + 8 M），数字与断言组数**永远一致**，删除/新增用例无需同步维护。

### LOW-6（环境变量展开递归）— **已修复 ✅**

- **修复方式**（handler.py 224-239 行）：`_ENV_REF_RE.sub` 连续 2 轮（固定轮数，必然终止），使变量值内嵌套引用（如 HERMES_HOME 值本身含引用形态）同样展开，避免保护基准漂移；未定义变量保留原样；
- **证据（独立复测）**：
  - 两层嵌套：设 A 值含 B 引用、B 值为受保护目录 → `_expand_env("%A%/config.yaml")` → `D:\myagent\.hermes/config.yaml` ✅（两轮语义正确）
  - 自引用：设 SELF 值含 `$SELF/x` → `_expand_env("$SELF")` → 固定两轮后 `'$SELF/x/x'`，**必然终止、无死循环** ✅
  - `re.sub` 的 repl 函数返回值不再被本轮重新扫描，替换语义正确；
- **小瑕疵**：注释「自引用形态在第二轮后保持原样」措辞略不精确——实际每轮会再展开一层（值增长），但「必然终止」断言正确（固定轮数），属注释级问题（列入建议-3）。

---

## 2. 回归与质量核验

| 检查项 | 结论 | 证据 |
|---|---|---|
| 测试全量通过 | ✅ | 实测退出码 0，`ALL PASS (29 scan + 4 hook + 77 new)`，110 断言组全绿（含既有 102 组 TC-A-01~47/TC-B/S/E/M 原样通过 + 新增 TC-A-48~55） |
| C 项迁移零改动 | ✅ | git diff e2ce1cd `on_pre_tool_call` vs `_guard_tmpdir`：仅签名行/docstring/EOF 空行 3 处差异，函数体逐行一致 |
| A/B 原有形态无回归 | ✅ | TC-A-01~47、TC-B-01~06、TC-S、TC-E、TC-M 全部原样通过；`&&`/`;` 分段、tee、重定向、cp、sed -i、dd of=、读形态等独立复测均与修复前行为一致 |
| 无未用 import | ✅ | handler.py 仅 logging/os/re（均使用）；test_handler.py 仅 importlib.util/sys/os/logging（均使用） |
| 无死代码 | ✅ | `_call_content`（MED-1 修复后有效调用）、`_OUTPUT_FLAG_EQ_RE`（两处使用）、`_prev_command_word`（tee 判定）均生效；无遗留失效分支 |
| 样式/命名/注释 | ✅ | 新增代码与既有风格一致（中文注释、常量集中、正则来源标注）；MED-1/MED-2/LOW-1/LOW-2 修复处注释均说明修复原因与设计依据，注释质量良好 |
| 新增用例质量 | ✅ | TC-A-48~55 覆盖 8 条 findings 对应形态（管道、动态 cd、os.open 写/读、curl -o 拦截/负例、wget/sort/--output=、未知命令低误拦），拦截与放行成对，断言方式与既有用例一致 |

---

## 3. 改进建议（非阻断，PASS 裁决后可选处理）

**建议-1（优先，fail-open 方向）— MED-2 残余漏拦：短选项参数粘连形态未识别**
- 位置：handler.py 408-411、519-526 行；
- 现象：`curl -o"<受保护路径>"` / `wget -O'<受保护路径>'`（引号直接粘连，无空格无 `=`）→ 放行。`_PATH_TOKEN_RE` 将 `-o"..."` 视为单 token，`_OUTPUT_FLAG_EQ_RE` 需 `=` 分隔不匹配，归一化后不命中。POSIX 短选项参数粘连（`-oPATH`）为合法 shell 写法，`curl -o<路径>` 无空格形态同样漏拦（实测 `--output="..."` 因有 `=` 则命中，存在形态间不一致）；
- 影响：需同时满足「curl/wget/sort + 短选项粘连 + 受保护路径字面」才触发，真实攻击面极小；但属静态明确写语义，与 MED-2 修复目标同源；
- 建议：对 token 做 `^-o`/`^-O` 前缀剥离 + 引号剥离后再归一化判定（低成本），并补一条 `-o"<路径>"` 用例。

**建议-2（fail-closed 方向）— MED-2 误拦：命令名出现在 echo/printf 参数文本中**
- 位置：handler.py 455 行 `_OUTPUT_FLAG_CMDS_RE.search(before)` 全文搜索命令名；
- 现象：`echo curl -o <受保护路径>`、`echo wget -O <受保护路径>`、`echo sort -o <受保护路径>` → 均判写拦截（实测）。实际仅打印字符串、不写文件；
- 影响：误拦方向无安全影响，但违背 Q-03 低误拦承诺；场景罕见；
- 建议：命令名判定改用 `_command_word(seg)`（段首词 ∈ {curl, wget, sort}）替代 before 全文搜索，并补 echo 负例用例。

**建议-3（注释措辞）— LOW-6 注释「自引用形态在第二轮后保持原样」略不精确**
- 实际每轮对残留引用再展开一层（自引用值会增长），「必然终止」断言正确（固定两轮）；建议措辞改为「固定两轮上限，自引用在轮数耗尽后保持残余形态」。

**建议-4（接受边界）— LOW-2 目录名含 `$` 字面被当作未解析引用放行**
- `cd D:/my$agent/x` → 放行；属 Q-03「无法可靠判定 → 放行」语义，无安全影响，与设计一致；如追求更严格可要求目录名存在性校验（不建议，违背纯内存约束）。

**建议-5（测试补充）** — TC-A-52~55 可再补：`-o"<路径>"` 引号粘连形态、`echo curl -o <路径>` 负例、`--output-document` 空格分隔形态、路径含括号 os.open 用例（当前套件均未覆盖）。

---

## 4. 结论

- **总体裁决：PASS** —— review-001 的 8 条 findings 全部真实修复并经独立实证（MED-1/MED-2 核心形态、LOW-1/LOW-2/LOW-4/LOW-6 代码修复、LOW-3 注释声明、LOW-5 为设计文档修订项不在本轮代码复审范围）；修复未破坏既有 102 断言组（实测 110 全过），C 项迁移零改动成立，无新引入的未用 import/死代码/样式退化；新发现问题均为罕见场景的低危形态边界，不阻断验收；
- **建议处理顺序**：建议-1（fail-open 残余）优先，建议-2 次之，其余可选；处理与否均不影响本 PASS 裁决，但建议在下一迭代回填。

---

### 复审统计

- 总体裁决：**PASS**（HIGH=0、MED=0、LOW=0 新增阻断项；改进建议 5 条非阻断）
- 8 条 findings 修复核验：全部 ✅
- 测试基线：退出码 0，ALL PASS（29 scan + 4 hook + 77 new = 110 断言组），77 与运行时自增一致
