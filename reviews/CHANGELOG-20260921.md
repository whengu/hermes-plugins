# write-guard 修订记录（CHANGELOG）

本文件承载 handler.py / test_handler.py 的**修订史与缺陷考古**。
代码注释只保留"为什么这样设计"，"曾经错在哪"一律记在这里。
行号以本文件建档时（2026-09-21）的 handler.py 为基准，后续会漂移，按符号名检索。

---

## 2026-09-22 round6（round5 双路复审修复，deleg_aed825ca）

**round5 复审**：sa-1 质量 CHANGES REQUIRED（轻量，阻断 F-Q1/F-Q2）；sa-0 安全
撞输出上限未交卷，但落盘实测（r5_a 全 replay 通过、r5_b/c/d/e 探针）有实锤：
D1/C3/C4。双路一致确认：round5 修复 9/10 到位、无行为回潮。

**修复项（TC-R6-01~11 锁定）**：
- **D1（HIGH 级）**：profile 镜像目录（<home>/profiles/<p>/plugins/write-guard/）
  不在反缴械保护面——write_file/patch/cp 可改镜像 handler.py，profile 会话直接
  加载被缴械副本。_is_guard_dir_target 泛化（home 树内任意 plugins/write-guard
  段）+ _is_protected_config 镜像插件代码分支 + 收集面同步；镜像目录读仍放行。
- **C3（MED）**：`cp --target-directory <dir>`（长形/=粘连/短形簇 -rt）旁路
  -t 判定——_COPY_T_RE 补长形词与 `$` 分支（before 已 rstrip，词尾=串尾），
  `=` 粘连目标 token 提取 + 分支认 raw 前缀；cp -T（GNU 不建目录）不误扩。
- **C4**：复制族末位=home 内目录（无尾分隔符，Windows 合法省略）与带斜杠形
  名实分叉（前者 PASS 后者 approve）——收集面把 home 内末位目录 token 送矩阵，
  统一 approve；mv（改名族 OOS-09）与读命令仍放行。
- **F-Q1（MED 文档名实）**：robocopy 撤出登记的"仍有绝对路径 token+矩阵分支
  兜底"承诺句实测不成立（robocopy 写配置零兜底）——改写为如实的零覆盖声明
  边界；TC-R5-15 锁 PASS 语义不变。
- **F-Q2（MED deploy）**：mirror_to_profiles 失败路径裸抛/半写/误报"已镜像"——
  逐文件 .tmp→os.replace 原子换入，OSError 受控捕获，失败不打印成功。
- **F-Q4（LOW）**：`subprocess.getstatusoutput(...)` 限定形漏一词（from-import
  形与 os. 限定形均有）——_SUBPROC_CALL_RE 名单补齐。
- **微疵**：F-2 恒死兜底支删除；L553 陈旧注释合并；TC-E70 标题改为
  "幻觉 cwd=F-6 防御纵深超集"（F-Q6a，原"C-cwd"名不副实）。

**登记补记（F-Q3/Q5/Q6，接受边界不修）**：
- F-Q3：star-import 后用户 `def run()` 覆写仍按 subprocess 语义扫（名字可能
  被重绑、静态不可知，fail-closed 同 F-8 族）——接受。
- F-Q5：`~` 展开=真实家目录（本机 C:\Users\guwh），`cp evil ~/x` 型跨家形态
  不命中单根归一化=设计后果非漏洞；xcopy 目标位语义（目录强制/文件问询）
  需专属解析——降声明边界（同 robocopy 论据）。
- M-3 会话级 cd 漂移（R4-6）：插件判定基准=进程 cwd，平台会话 cd 记录漂移时
  有落差——维持接受边界（常态一致）。
- F-Q6 余项（R4-3 dict 形读参数假阳性、tar 行理由扩写）并入本条：
  dict 形写工具参数按写处置=保守方向；tar/ln 落点绕过与改名族（L4/OOS-09）
  同源不扩——维持登记。
- sa-0 撞输出上限教训：round6 派单要求"结论先写、报告落盘、终答复述"。

**基线**：ALL PASS 29+4+219（+11 条 TC-R6）。
## 2026-09-22 round5（round4 双路复审修复，deleg_6dc70025）

**round4 复审**：sa-0 安全 CHANGES REQUIRED（F-1~F-8 + OBS-1/2）；sa-1 质量
CHANGES REQUIRED（R4-1~R4-6，阻断三项 R4-1/R4-2/R4-5）。双路收敛一致处：
round3 修复主体真到位（六项中 C-1/N-4/N-5 完全过、五/六重放通过），扣分集中
在"修复引入的同类新面"。

**修复项（TC-R5-01~16 锁定，28 场景复验全过）**：
- **F-1（HIGH，H-1 同源再犯）**：`cp evil <home>/plugins/write-guard`（无尾
  分隔符，Windows 与带斜杠同语义）旁路反缴械——新增 _is_guard_dir_target，
  复制族/-t/收集面三处接入；无尾分隔符的守卫目录目标一律按写处置。
- **F-2**：workdir 相对形态未绝对化（`workdir="../.hermes"` + 相对写旁路）——
  判定基准先过 _normalize_path（相对进程 cwd，与平台 shell 常态一致）。
- **F-3（=R4-2）**：from-import 门留同类逃逸（别名 as r / star import * / 多行
  括号 / import subprocess as sp 全漏）——门重写覆盖四形态，负例零误拦保持。
- **F-4（=R4-5）**：robocopy"并入复制族"是半匹配假覆盖（src <dir> <file> 目标
  在第2参）——**撤出** _COPY_CMDS，降声明边界（CHANGELOG+代码注释+TC-R5-15
  锁 PASS 防漂移）。与 round3 拒绝 spawn 族的自家论据对齐（名实一致）。
- **F-5**：_DD_RE/_SED_PERL_RE 缺 IGNORECASE（大写 SED/DD/PERL 漏拦，同族
  _PS_WRITE_RE 有）——补齐。
- **R4-1**：rsync 的 -t 是 preserve-times 不是目标目录，误拦纯读形态——
  -t 分支限 cmd in (cp, install)。
- **F-6**：cwd 死键参与 C 扫描=防御纵深超集（幻觉 cwd=/tmp 被拦，fail-closed
  可接受）——注释补记决策理由。
- **F-7**：args 非 dict → 三守卫连抛被项级隔离吞掉整链放行（round2 同类
  fail-open 残面）——入口收敛 args = {} 走完整链。
- **OBS-1（部署面）**：平台插件发现只扫 get_hermes_home()/plugins，profile
  会话（hermes -p developer/architect）加载各自 profiles/<p>/plugins/ 下的
  **v1.0.0 陈旧副本**=round2/3/4 保护在 profile 会话不存在——deploy.py 新增
  mirror_to_profiles：主部署后镜像同步**已存在** write-guard 目录的 profile
  （不凭空给未安装 profile 装守卫）。
- **R4-4**：_SUBPROC_BARE_RE_TMPL 死常量随 F-3 重写移除（AST 全模块复扫零
  未用顶层名）。

**未修（登记边界）**：F-8 两向（docstring 升格误拦=fail-closed 方向接受；
相邻字面量拼接漏=需 AST 级解析，违背不加复杂度）；M-3 会话级 cd 回退落差
（R4-6，平台 _resolve_command_cwd 有 session-cwd 记录，插件回退进程 cwd——
常态一致，漂移场景登记不修）；tar/ln 束（N-8，理由已登记）。

**基线**：ALL PASS 29+4+208（+16 条 TC-R5）。
## 2026-09-22 round3 复审修复（deleg_87a156db 双路复审：sa-1 CRITICAL/HIGH + sa-0 N 系列）

**阻断项（已修，TC-R3-01~16 回归锁定）**：
- **C-1/N-2 CRITICAL**：round2 的 C-cwd 修复扫 `args["cwd"]`，但平台 terminal 真实
  参数名是 `workdir`（terminal_tool 签名实证）——修复打在不存在键上=零效果假绿，
  回归用例跟着错坐标自证通过。修正：workdir+cwd 并收；A 面以 workdir 为相对路径
  判定基准。教训：**修坐标类缺陷必须对平台 schema 实证，测试必须用真实参数形态**。
- **H-1 HIGH**：`cp evil.py <home>/plugins/write-guard/` 放行（F-A7 只认"目标==home
  本身"，home 内子目录整体漏）。修正：末位参数为 home 内目录形态（原始串以分隔符
  结尾）→ 复制目标写面，经处置分流归 approve；`cp -t <子目录>` 同步放宽。
- **N-4**：M-1/F-A2 内嵌递归丢失 cwd 基准（顶层 block、`bash -c "echo x>config.yaml"`
  +workdir 却放行）。三处递归调用点补 base_cwd/base 传递。
- **N-1**：os.system 提取族补 getstatusoutput；`from subprocess import run` 裸词形态
  加 from-import 门扫描（无该 import 不扫，防误拦业务 run()）。
- **N-3**：三引号字面量击穿写正则——入口折叠归一（三引号折成单引号后再判定）一处
  解决，替代 6 条正则各自支持三引号的后向引用复杂度。
- **N-5**：代码内工具调用补位置参（write_file(CFG,'evil')）与 dict 形（'path': CFG）。
- **N-6 保守子集**：rsync/robocopy 并入复制语义（复用末位=目标分支，零新逻辑）。

**按"不加复杂度"降为声明边界（不做，理由记录）**：
- os.spawn*/os.exec* argv 族：首参=程序路径、写目标散在 argv 后部，单参捕获只会
  半匹配（把程序名当命令行）形成假覆盖；正确判定需 argv 语义解析。
- tar -C/unzip -d/patch <cfg>/ln -sf/find -delete：目标位含选项语义或属链接/改名族。
- exec/eval 字面量套壳降 approve（N-7）：共现启发式误拦成本>收益，不做。
- tool_call(name=...) 泛化分发套壳（N-5 尾部）：等同"运行时才知道调用什么"，
  归入变量拼接声明边界。
- M-3 会话级 cd 跨调用跟踪（第1次 cd <home>，第2次相对写）：需按 task_id 镜像平台
  会话 cwd 状态，引入状态管理复杂度；且 execute_code 无 workdir 参数（schema 实证，
  sa-0 该项建议坐标不成立）。维持单命令静态判定为声明边界。

**过程事故（如实记录）**：
1. 主会话曾误报"TC-A-55 回归失败"——实测全链 None=放行，不存在回归。修复验证
   必须跑原始场景，不能凭日志片段下结论。
2. _r3c 脚本半途崩溃导致 handler.py 一度处于"写入但未编译"的中间态（非原子），
   后续以行级幂等重建恢复。教训：改文件脚本必须先 compile 再落盘。

测试基线：ALL PASS（29 scan + 4 hook + 192 new）。
## 2026-09-21 round2 复审修复（deleg_87a156db/sa-1 质量复审报告，CHANGES REQUIRED 后）

| 编号 | 级别 | 缺陷（复审实测复现） | 修复 |
|---|---|---|---|
| M-1 | HIGH | `bash -c "echo x>cfg"` / `pwsh -Command` / `cmd /c` —— terminal 段的内嵌 shell 载体全线放行（F-A2 只封了 execute_code→shell 方向，terminal→内嵌 shell 方向没封） | `_EMBED_SHELL_RE` 识别解释器命令词 + -c/-lc/-Command//c//k 引号体，递归 `_judge_terminal`（复用深度上限）；处置分流在递归链内保持（内嵌 cp 仍 approve） |
| M-2 | MEDIUM | `open(cfg,'w',encoding='utf8')`、`open(cfg, mode='w')` 放行——正则强制双参收尾 `\)`，合法高频写形态漏判 | 第二参后允许 `,`/`)` 收尾 + `mode=` 命名形可选前缀 |
| M-3 | MEDIUM | terminal 显式 `workdir` 参数未参与判定基准（平台 per-command cwd 优先，插件恒用进程 os.getcwd()）→ `workdir=home + 相对路径写` 落差漏判 | `_judge_terminal(base_cwd=args["workdir"])`，与平台 `_resolve_command_cwd` 优先级一致 |

第一轮 sa-1 修复验收结论：S-0/S-1/S-2/T-3/T-4/T-5/R-7/R-8 全部 **已修**（复审 AST/实测复核）。
过程记录：本轮修复自验方式=先跑复审方留下的复现脚本（`_dbg_m.py`，修复前 6 项
中 5 项放行、修复后 8/8 符合预期），再补 12 条回归用例（TC-M101~M122），
全量 ALL PASS（29+4+176）后才提交（git 5d93150，09-21 工作首次入库，D-5 处置）。

## 2026-09-21 sa-0 对抗安全走查修复（deleg_b5774fc6/sa-0，实测证据）

| 编号 | 绕过路径（实测复现） | 修复 |
|---|---|---|
| F-A1 | `open(r'...config.yaml','w')`——r/b/f 字符串前缀击穿 open/Path/os.open/shutil/tool_call 全部写形态正则（原正则要求 `(` 后紧跟引号） | 6 条正则统一容忍 `[rbfuRBFU]{0,2}` 前缀；open 改命名组 |
| F-A2 | execute_code 内 `os.system('echo evil> CFG')` / `subprocess.run('cp a CFG', shell=True)` 零检测——shell 面整族旁路 A 守卫 | `_OS_SYSTEM_RE` / `_SUBPROC_CALL_RE` 提取字符串命令文本（list 形态逐项拼接），递归复用 terminal 判定链；`_NEST_DEPTH_LIMIT=3` 防 terminal↔execute_code 互递归 |
| F-A3 | **守卫自身源码**（`.hermes/plugins/write-guard/handler.py`）可被 write_file 直接改写（.py 不在保护集）→ 一切保护可被缴械 | `plugins/` 下 .py/.yaml/.yml 纳入受保护；开发通道不受影响（workspace 可写、deploy.py 命令文本不含受保护字面量） |
| F-A4 | `sed -i.bak` / `--in-place=.bak` 漏判（旧正则要求 `-i` 后是空白/行尾） | 短形改负向断言 `(?![\w-])`；补 `--in-place` 长形态 |
| F-A5 | `truncate -s 0 CFG` 不在写矩阵 | truncate 命令词 → 写 |
| F-A6 | `pwsh -c Set-Content -Path CFG` 不在写矩阵 | Set-Content/Add-Content/Out-File（大小写不敏感）出现在受保护路径前 → 写 |
| F-A7 | `cp x <home>/`、`cp -t <home>`：目标是**目录本身**，`_is_protected_config` 对目录早退 False，token 根本进不了候选收集 | terminal 面收集扩展 home 目录本身；矩阵 cp 分支识别目录目标。边界收紧：**原 DR-25「cp 至目录 → 放行」被 sa-0 证明正是绕过「cp 目标文件」检测的写法**，按用户「cp 弹审批」决策翻转为 approve（TC-A-46 同步翻转）；读方向（cat/ls 目录）不受影响 |
| C-cwd | terminal 的 `cwd` 参数可指向 /tmp 而 command 干净 → C 对该参数零扫描 | C 守卫对 terminal 增扫 cwd 参数 |

**过程事故（如实记录）**：F-A7 实现中调用点误传作用域外变量 `pipe_cwd` →
`NameError` 被守卫项级异常隔离吞成 **fail-open**（A 项 terminal 路径整体静默
失效、返回值 None=放行）。11 个既有用例当场捕获。教训：**异常隔离会把实现
bug 转化为保护失效，测试套件是它之下唯一防线**——新增判定分支必须先落测试。

**声明的接受边界（本轮不修，理由如下）**：
- HERMES_HOME 环境变量被进程外改往他处 → 保护基准整体漂移。模型无法修改
  gateway 进程环境，属运维治理面，非插件可防御（插件若拒绝跟随环境变量，
  则 profile 多实例场景失效——DR-05 实时读取是有意设计）。
- Windows 8.3 短名（MYAGEN~1）、目录尾点、junction 中转：需文件系统级解析
  （IO + 平台调用），与 NFR-05 纯内存判定设计冲突；NTFS 上 8.3 名默认多为
  禁用状态。若实际威胁出现，另立项评估。
- 非扫描工具集（process_manage.write、chrome_upload_file、connector 面写
  工具等）不经插件：Hermes 无统一"落盘前"hook，插件只能白名单式覆盖已知写
  工具；每新增写工具需人工评估补入（维护契约，同 _READ_TOOLS 快照提醒）。
- execute_code 变量拼接/动态构造路径（`open(p)`，p 来自运行时）无法静态判定
  → 放行（Q-03 设计本意：静态守卫防错不防恶意）。

## 2026-09-21 质量修复轮（独立工程质量审查 deleg_b5774fc6/sa-1 后）

| 编号 | 问题 | 处置 |
|---|---|---|
| S-0 | plugin.yaml description 只描述临时目录拦截（v1.0 时代），且 version 停留 1.0.0 未反映 09-17 扩展与 09-21 决策 | manifest 重写为四项守卫总览；version → 1.2.0 |
| S-1 | 注释内嵌决策考古（B1~B5 / MED / LOW / TC-A-62 修订史与判定逻辑混居） | 历史迁入本文件；代码注释只留设计理由。手术经 AST 等价校验（去 docstring 后与术前备份逐字节一致），行为零变化 |
| S-2 | `_approve_result` / `_config_block_result` 重复实现"变体命中双段展示" | 抽 `_shown_path()` 公共 helper；两函数保留（返回 shape 不同：approve 带 rule_key，block 不带，语义差异有意保留） |
| T-3 | test 用 `handler.GUARDS[i]` 硬索引替换桩守卫，守卫增删即静默错位（守卫 D 插入曾致 6 用例连锁失败） | 改 `_stub_guard(name, fn)` contextmanager，按 `__name__` 定位；函数名成为测试契约 |
| T-4 | 清单不变量测试与"5 项快照"混在一条断言 | 拆为 TC-C1-13（安全不变量，恒真红线）+ TC-C1-14（清单快照，变更提醒） |
| T-5 | hook 用例数 `4` 硬编码进收尾文案 | `_hook_cases` 列表 + `HOOK_N = len(...)` |
| E-3 | 原 TC-E-03 用 `hindsight_retain` 测"A 异常后继续轮询"，但 retain 不经过 A，测不到该语义（假绿） | 改用 `write_file + _CFG`（A 真实命中且抛异常）验证续轮询 |
| R-7 | deploy.py 一致性校验自指（copy 后比对必然相等）、py_compile 外抛裸 traceback、路径硬编码 | 复制前锚定源 sha256、部署后比对快照；subprocess 返回码判定；SRC/DST 支持 argv 覆盖 |
| R-8 | `_ENV_EXPAND_ROUNDS` 魔数、判定热路径内联 `re.xxx` | 命名常量；14 处内联正则预编译进 ②模式编译区 |
| P-10 | `_terminal_position_is_write` 的 `norm` 参数从未使用 | 删除该参数（`_guard_*` 的 `task_id` 是四守卫统一签名，保留） |

## 2026-09-21 对抗性安全走查（deleg_fdfaf47f）修复项

| 编号 | 原缺陷（可绕过路径） | 修复 |
|---|---|---|
| B1 | `~` / `~/...` 形态路径不做展开 → 与归一化后的 HERMES_HOME 比对失配，`write_file ~/../.hermes/config.yaml` 类写法绕过 | `_normalize_path` 增加 `os.path.expanduser("~")` 展开，与 Hermes 侧 `get_subprocess_home()`（`tools/file_tools_paths.py::_expand_tilde`）语义对齐 |
| B2 | 受保护判定只看文件名含 `config` 子串 → `profile.yaml` / `settings.yaml` / `.env` / `*.json` 完全不设防 | `_is_protected_config` 扩为：HERMES_HOME 内 + 扩展名 yaml/yml/json 或文件名含 config 或 `.env` 系列（用户决策「范围要扩大」） |
| B3 | terminal / execute_code 写配置一律 approve，与"仅记忆写要审批"的用户要求冲突 | 新增 `_config_write_disposition()` 分流：cp/copy/install/shutil.copy 类 → approve（用户明确"cp 是改配置文件的方法，要弹审批"）；echo>/>>/tee/sed -i/dd of=/curl -o/open('w')/write_text/os.open 写标志/代码内 write_file 调用 → block |
| B4 | MSYS 路径 `/d/myagent/.hermes/config.yaml` 不做转换 → 与 `d:/...` 归一化结果不等，绕过 | `_MSYS_FULL_RE` + `_MSYS_DRIVE_RE` 双条件：`/x/` 单盘符与 `/cygdrive/x/`、`/mnt/x/` 形态转 `x:/`；单字母判定避免误伤 `/tmp` 等 POSIX 根路径 |
| B5 | Windows verbatim 前缀 `\\?\`、`\\.\`、`//?/` 不参与归一化 → 同一文件不同写法，绕过 | `_VERBATIM_PREFIX_RE` 剥离前缀；**必须**在 `_unescape_string_literal` 与连续斜杠压缩**之前**执行（否则 `\\` 被解义、`//?/` 被压成 `/?/`，正则失配——本条曾三次返工，教训：归一化步骤顺序是正确性的一部分） |
| L4 | `shutil.move` / `os.rename` / `os.replace` 目标为配置时不拦 | 用户决策「改名和复制不拦截」→ 保持放行（OOS-09 路径级操作语义），TC-A-64/65/66 锁定 |
| A 守卫语义 | write_file / patch 写配置走 approve（弹卡可放行） | 用户决策改为 block 直接截断，消息指引 safe-config-modify skill |
| C 守卫 | 读工具参数含 `/tmp` 字样被误拦；白名单曾膨胀到 14 项 | 用户决策收敛为 5 项定案：`read_file` / `search_files` / `web_search` / `hindsight_recall` / `hindsight_reflect` 无条件放行，其余工具一律走参数检查 |

## 2026-09-21 `_unescape_string_literal` 重写（隐藏最久的缺陷）

**症状**：`write_file(path=r"D:\myagent\.hermes\tui-theme-boot.json")` 被放行，而 `profile.yaml` 正常拦截。测试 TC-A-62 持续失败但手改小脚本复现不一致，排查成本高。

**根因**：旧实现按 C/Python 转义语义解义**单反斜杠**序列，`simple` 表含 `"t": "\t"`、`"u"` 分支等。Windows 路径里 `\t`（`\tui-theme-boot.json` 的前缀）被解义成 **tab 字符**、`\u` 被解义成 **unicode 转义**，归一化结果变成含控制字符的乱码路径 → 与受保护前缀不等 → 保护静默失配。凡路径段以 `t/u/n/r/a/b/f/v/0-7/x` 开头的 Windows 反斜杠路径全部中招（`\temp`、`\new`、`\users` …）。

**修复**：只解义**成对双反斜杠**（`_DOUBLE_BACKSLASH`，terminal 命令引号内的转义写法）为单反斜杠；单反斜杠 + 任意字符一律按字面路径保留。原 `_ESCAPE_SEQ_RE` 随之废弃删除。

**教训（写入设计原则 DR-22 修正）**：路径归一化的输入是"用户/模型写的路径文本"，不是"待求值的 Python 字符串字面量"。把两者混为一谈会让安全判定依赖于字符串转义语义——安全边界上不允许这种依赖。

## 2026-09-21 守卫 D：gateway 生命周期命令禁令

- 触发：助手两次未加载 gateway-restart skill 就凭记忆执行 `hermes gateway restart`（用户拒绝并震怒）；该命令本身也在 Hermes 危险命令清单内（会杀掉运行中的 agent）。
- 决策：`hermes gateway restart|run|start` 一律 block，不进审批（防止"批准"成为误操作通道）。`status` 查询允许；`stop` 未在用户禁令清单内 → 放行。
- 消息为固定文案（用户指定原文，不做插值）："你违反了用户的规则, 必须使用skill指定的方式来访问hermes gateway"
- 边界（有意为之）：按命令文本匹配，`grep 'hermes gateway restart' docs/` 这类提及也会 block。理由：守卫 D 若放过引号内的嵌套执行面（`bash -c "hermes gateway restart"`）就形同虚设，而精确区分"引用 vs 执行"需要 shell 解析，成本高于收益 → 宁可多拦，用户改写法即可。此与守卫 C 的"纯文本提及放行"边界不同，属两处守卫的不同设计取向。
- 定位：防呆层（防错不防恶意）。变量拼接（`V=restart; hermes gateway $V`）、base64 混淆等刻意规避不在覆盖范围。

## 2026-09-17 扩展初版（配置写保护 + 记忆写保护）

见 `design/design.md`（设计）、`requirements/requirement.md` v1.1（需求）、
`reviews/review-001.md` / `review-002.md`（两轮独立代码走查，13 条 findings 及其测试回挂）。
历史评审文件为**时点快照**，不随后续决策回改。
