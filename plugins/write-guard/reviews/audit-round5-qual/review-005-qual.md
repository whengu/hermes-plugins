# write-guard round5 质量复审报告（只读，2026-09-22）

| 项 | 值 |
|---|---|
| 被审对象 | git 4d08ddd（工作区=HEAD 实证：`git diff 4d08ddd` 空）；主部署 handler.py 哈希 `70bc5d4d…` = 工作区一致 |
| 方法 | 只读；实跑 test_handler.py（**ALL PASS 29+4+208 复核属实**）、_verify_r5.py（28/0）、_verify_r3.py（25/0 无回归）、round4 四脚本重放；AST 死码扫描（dead=[]、unused fns=[]、GUARDS 序不变）；新增对抗探针 r5_q_attack.py（30 例，本目录）+ 补充定向实测 14 例 |
| 纪律 | 不采信自述：round5 全部修复逐条以原始场景重跑；profile 镜像一致性以磁盘哈希实证 |

---

## 一、round5 修复项逐项验收

| 项 | 判定 | 证据与工程质量 |
|---|---|---|
| **F-1**（HIGH，反缴械无尾分隔符） | **已修** | _verify_r5 7/7：`cp evil <guard>`（正/反斜杠、引号包裹、`-t` 形、os.system 内嵌形、大小写混排 `PLUGINS\Write-Guard`）全 approve；负例 cat/ls 放行。三处接入点（末位分支 L644、-t 分支 L657、收集面 L804）齐。前缀误伤攻击：`cp -t D:/x/write-guard-old`（同名前缀目录）→ 不误按守卫处置（L603 `_SEP` 边界拼接正确）。**残留**：`~/.hermes/plugins/write-guard` 形态仍 PASS——非修复缺陷（本机 `expanduser('~')=C:\Users\guwh`，与 D 盘 home 本不同根；插件归一化**单根**设计使 MSYS/verbatim/%HERMES_HOME% 形均折叠命中，唯 `~` 展开落他家目录属设计后果），建议 CHANGELOG 补一句声明（LOW，见新 finding 表 F-Q5）。 |
| **F-2**（workdir 绝对化） | **已修** | `workdir="../.hermes" + echo>config.yaml` → block；绝对形仍 block；负例 workdir=workspace 放行；`bash -c` 嵌套 + 相对 workdir → block（递归基准链保持，N-4 不回潮）；`workdir="  "`（空白）不炸链；管道内 `cd ../.hermes &&` 正确深度 → block（初审探针误报系 kernel cwd 错位，钉死 `cwd=workspace` 后复验通过）。`or (wd if isinstance...)` 兜底分支为恒 False 死支（_normalize_path 对非空 str 实际不会返 None——防御性可留，注释宜说明，LOW 级微瑕）。 |
| **F-3**（门四形态） | **已修（带新假阳性面）** | 四形态全 block（as sp / run as r / import * / 多行括号）；两负例零误拦（业务 run() 无 import、无 import 裸 run、字符串内 "from subprocess import run" 不触发）；`from subprocess import getoutput as run`+`run(...)` 真别名亦 block；括号多行含 `run as rr` 亦 block。AST 复扫零死常量（R4-4a 的 `_SUBPROC_BARE_RE_TMPL` 已移除）。**新面**：`from subprocess import *` 后**用户自有 `def run()` 覆写**仍被按 subprocess.run 扫（B1 实测：纯业务代码 block）——star 语义即"名字可能被重绑"，静态不可知，方向 fail-closed 与 F-8 同类，未登记（F-Q3）。 |
| **F-4**（robocopy 撤出降边界） | **撤出已修；登记注释名实不符** | `robocopy src <home> config.yaml` → PASS（与"降声明边界"一致，TC-R5-15 锁 PASS 防漂移，方向正确）。但 handler L559 与 CHANGELOG L26 均写「其写配置行为仍被**绝对路径 token + 其余矩阵分支**兜底」——实测 `robocopy src <home>/config.yaml`、`robocopy src <guard>/handler.py`（robocopy 真实语义即覆写该文件）全 PASS：robocopy 不在 _COPY_CMDS，矩阵无兜底分支，末位 token 是文件名非目录、H-1 腿也不触发。**登记句承诺了不存在的覆盖=round4 点名的"声明与实效分叉"同型**（F-Q1，见三节）。 |
| **F-5**（IGNORECASE） | **已修** | SED/DD/PERL 大写 -i/-pi/of= 全 block；负例 `SED -n '1p'`（大写只读）放行；`DDof=` 粘连词边界不拦与 round4 修法约定一致（词级防呆层边界）。 |
| **F-6**（cwd 死键注释） | **已修** | L188-190 注释落地，理由（幻觉参数 fail-closed 可接受）与 F-6 原始建议逐字对应。 |
| **F-7**（args 非 dict） | **已修** | None/"str"/[1]/42 四种畸形参数均无异常、无 traceback、整链 None=放行；TC-R5-16 锁定。 |
| **R4-1**（rsync -t） | **已修** | `rsync -t CFG backup/` 放行；`rsync -t a.yaml CFG`、`rsync -a -t src CFG` 写方向仍 approve；`install -t <guard>` 拦；`cp -t 非home目录` 不误伤。`("cp","install")` 门与 _COPY_CMDS 中 "copy" 无 -t 语义相符（cmd copy 无 -t）。 |
| **TC-R5 16 条** | **已落** | run_r5_fixes 16 条全绿，覆盖 F-1×4/F-2×1/F-3×5/F-5×3/R4-1×1/F-4×1/F-7×1；_verify_r5 另 12 条独立重放全过。 |
| **OBS-1**（profile 镜像） | **已修且实效达成** | 见二节。 |

## 二、deploy.py mirror_to_profiles 工程审查（重点 2）

**一致性实跑验证（当前态）**：主部署与 `profiles/{architect,developer}/plugins/write-guard/` 三文件（__init__.py / handler.py / plugin.yaml）**逐文件 sha256 全 SAME**（handler `70bc5d4d`），两处 profile 目录无 `__pycache__` 残留；round4 实证的 v1.0.0 陈旧副本（4296B）已消除。profile 目录恰为 FILES 三件=镜像原子完整。

**路径推导**：`dst.parent.parent/"profiles"` 硬编码 `<home>/plugins/write-guard` 布局假设。沙盒实测：dst 摆错位（`<x>/a/plugins/write-guard`）→ 推导漂到 `<x>/a/profiles`，不存在则打印跳过返回 0——**错位方向静默不炸、不误写他家目录**（E1/E5 实证），可接受；但 dst.parent.parent 恰有 profiles 目录的错位会镜像到**非 HERMES_HOME 的 profiles**（沙盒 E1 之反面构造需 dst 恰好两跳，真实部署不存在此态，不立 finding）。

**与主部署校验顺序**：镜像在 [4/4] 哈希校验全过之后执行（main L90），源取"刚校验过的主部署"（L117 注释属实）——顺序正确，不会把未校验内容扩散。

**失败路径缺陷（F-Q2，MEDIUM·部署工具面）**：
1. 每个 profile 的 **`shutil.copy2` 逐文件裸调用零 try/except**（L118）：实测目标 handler.py 置只读 → `PermissionError` 裸 traceback 外抛，越过函数自身"哈希失败返回 None→main 1"的受控失败协议，也背离本文件 R-7 轮确立的"subprocess 返回码判定、不外抛裸 traceback"纪律；
2. 失败时**半写**：3 文件写到第 2 个抛错/校验不一致即中断，profile 停留在混合版本（无 staging/回滚），而"陈旧副本顶掉主部署"正是 OBS-1 要防的事故——半写=同类腐化的新引入路径；
3. `ok=False` 后不 break，继续拷剩余文件（放大不一致窗口）。
4. 小疵：L125 `已镜像 profile[...]` 在 ok 判定**之前**打印——校验失败时输出"已镜像"+FAIL 自相矛盾。

## 三、登记边界条目核对（重点 3：名实一致 + 新修复是否再造分叉）

| 条目 | 登记 | 名实一致 | 
|---|---|---|
| F-8 双向 | CHANGELOG L43-46 升格登记，理由（fail-closed 接受 / 拼接需 AST 级）成立；实测 docstring 型仍 block（D1）、拼接型仍 PASS=与登记一致 | ✅ |
| M-3 会话 cd / R4-6 | L44-46 补记（平台 session-cwd 回退落差登记不修）；F-2 注释 L963-964 明确"不叠加"。实测 `cd <home>;` 跨调用无状态（单命令静态判定=登记语义） | ✅ |
| tar / N-8 | round3 L68-71 + 本轮沿用；round4 R4-6"理由半句"的扩写义务本轮**未做**（CHANGELOG 该节未动）——非阻断遗留 | ⚠ 遗留未补 |
| robocopy 三参（F-4 新增） | 有 CHANGELOG 条目 + TC-R5-15 锁定 PASS——**形式完整**；但"兜底覆盖"半句为虚假承诺（实测 3 形全漏，见二/一节）→ **round5 自身新引入的 CHANGELOG 与实效分叉**，正是本次复审点名要查的模式 | ❌ F-Q1 |
| N-7/spawn 族/tool_call 泛化 | 沿用 round3 登记，行为无漂移（os.getstatusoutput 仍 block 对照在） | ✅ |
| profile 镜像（OBS-1） | CHANGELOG L35-39 描述与实现一致（仅同步已存在目录、不凭空安装） | ✅（实现质量另计 F-Q2） |

**结论（重点 3）**：登记**完整性**达标（每条均有编号+理由+TC 或锁），名实一致**一处破口**：F-4 的兜底声明句——修复工程把"撤出"写对了，却给撤出项补了一句不存在的保护承诺。

## 四、同类腐化残留扫描（重点 4）+ 新 finding

AST 全模块：死常量 0、未用顶层函数 0（R4-4a/b 的缩进漂移位于旧 L826-838，本轮重写为单缩进规整体——复验通过）。重复字面量：`_COPY_CMDS` 单源三用；`_is_guard_dir_target` 收敛了 `"plugins"+"write-guard"` 字面量（L602 唯一出现点，good）；plugin.yaml description 未随 F-1~F-7 行为变化失真（四项守卫总览仍准确，version 1.2.0 沿用轮惯例）。注释矛盾扫描：F-2/F-6/F-4/R4-1 新注释与代码逐条对读，唯 F-4 兜底句失真（F-Q1）；L553-555 旧注仍写"rsync/robocopy 与 cp 同为复制语义"起头，紧接着 L556 才转折"不含 robocopy"——先陈旧事再自我否定，建议合并（微疵）。

**新 finding 清单**：

| # | 级别 | 内容 | 建议 |
|---|---|---|---|
| F-Q1 | MEDIUM（文档名实） | F-4 登记句"robocopy 仍被绝对路径 token+其余矩阵分支兜底"实测不成立（`robocopy src <home>/config.yaml`、`… <guard>/handler.py` 全 PASS） | 改写为"robocopy 目标位写配置当前零覆盖，属声明边界（需专属位参解析）"；TC-R5-15 已锁 PASS 语义不变 |
| F-Q2 | MEDIUM（deploy） | mirror_to_profiles 失败路径：copy2/哈希读裸抛（实测只读目标 PermissionError 外抛）、半写无回滚、失败仍打印"已镜像" | 逐 profile try/except → 受控返回 None；或先拷 `*.tmp` 后 rename 原子化；提示移入 ok 分支 |
| F-Q3 | LOW（假阳性面·登记即可） | star-import 后用户 `def run()` 覆写仍被 subprocess 语义 block（fail-closed 方向，同 F-8 族） | CHANGELOG 接受边界节补一句，不单修 |
| F-Q4 | LOW | `subprocess.getstatusoutput` 限定形漏（F-3 把该词收进 _SUBPROC_FUNCS 裸词表，_SUBPROC_CALL_RE L293 名单未同步含之；os. 限定形有、from-import 形有，独缺 `subprocess.` 直调） | 正则名单补一词一 TC |
| F-Q5 | LOW（声明补记） | `cp evil ~/.hermes/plugins/write-guard` 型跨家形态不拦（归一化单根设计后果，他机 `~` 即 `.hermes` 家时成立）；xcopy（Windows 原生复制，未登记未拦）同型 | 边界节各补一句 |
| F-Q6 | LOW（残留未清） | round4 OBS-2 点名的 test_handler L591-594 `cwd` 假坐标用例、R4-3 dict 形假阳性登记、R4-6 tar 行理由扩写——CHANGELOG L11 把 OBS-2 列入 CHANGES REQUIRED 输入，但 round5 修复清单未含此三小项，登记也未补 | 下轮随修或在本节明示"故意不随修" |

## 五、裁决

**CHANGES REQUIRED**（轻量，均为局部修复，无行为回潮）。

- round5 修复工程本体：**9/10 验收通过**——F-1~F-7、R4-1、OBS-1、TC-R5 16 条全部真到位，round4 全部原始场景重放封堵（_verify_r5 28/28、round4 四脚本复跑），208+29+4 无回归，AST 干净，profile 镜像两处实测逐字节一致；F-4 的"撤出"方向也正确。
- 阻断项仅两处：**F-Q1**（新登记句名实分叉——恰是本轮复审重点 3 要防的模式，被 round5 自己踩中一次）与 **F-Q2**（mirror_to_profiles 失败路径裸抛/半写）。F-Q3~Q6 为登记补记与一行级随修。

*证据脚本：reviews/audit-round5-qual/r5_q_attack.py（30 例，E4 只读注入仅作用于本目录沙盒文件，已复位权限）。全程只读，未触碰 handler/test/deploy 与部署目录。*
