# write-guard round4 质量复审报告（2026-09-22）

被审对象：git 69aafcf（工作区=HEAD、部署副本 DEPLOY-SAME、py 编译 OK）。
方法：只读。实跑 test_handler.py（ALL PASS 29+4+192）、_verify_r3.py（25/0）、
纯内存探针 reviews/audit-round4/_probe_r4.py（P1~P7）、AST 死码扫描 _ast_scan.py；
平台 schema 复核 hermes-agent@D:/Project/guwh（terminal_tool 签名、_resolve_command_cwd、
code_execution_tool 参数表、execute_code 子调用 RPC→handle_function_call 回环）。
行号以 69aafcf 为基准。

## 一、round3 修复逐项验收

| 项 | 判定 | 证据与工程质量 |
|---|---|---|
| C-1/N-2 workdir 真实坐标 | **已修** | 实跑 TC-R3-01~03 + 探针 P6 重放全符预期；平台实证 terminal_tool(workdir=…) 真实、schema 无 cwd；handler 两键并收（cwd 为良性超集），A 面 base_cwd 用 workdir+isinstance 守卫（L906-907）。坐标类缺陷“对 schema 实证 + 真实参数形态测试”教训本轮落实。残留缺口见 R4-6（会话 cwd 记录回退落差未登记） |
| H-1 目录目标 | **已修** | TC-R3-15/16、探针：cp 子目录/`cp -t` 子目录/profiles 子目录/approve；cat 目录、workspace 目录放行；缴械变体（末位=handler.py）approve。`raw.rstrip("\"'").endswith(("/", chr(92)))` 目录形态判定边界稳健。伴生缺陷 R4-1（`-t` 分支不分命令词）由本轮新代码面引入 |
| N-4 递归传基准 | **已修** | 三处递归点（_EMBED_SHELL L747-748 / os.system L817-818 / subprocess L846-847）base_cwd=base 传递完整；TC-R3-04 重放 block |
| N-1 getstatusoutput + from-import 门 | **不完整** | 正修：getstatusoutput 入 _OS_SYSTEM_RE；门方向正确——无 import 不扫、业务 run() 零误拦（TC-R3-07 + 探针）。但门本身引入同类逃逸（R4-2：as 别名 / 多行括号 import）；`_SUBPROC_BARE_RE_TMPL` 死常量、L836-838 缩进漂移（R4-4） |
| N-3 三引号折叠 | **已修（带新面）** | 入口折叠（L805-810）判定语义正确，TC-R3-08/09 + 探针 block；纯判定视图无副作用。新假阳性面：折叠后 docstring 文本与代码同视图，`"""…open(CFG,'w')…"""` 纯文档 → block（R4-3 同族）；另 `"""→"` 是无损归一（建议项） |
| N-5 位置参/dict 形 | **已修（带新面）** | 三形态齐（TC-R3-10~12）；正则交替顺序经手动派演安全（`write_file("path":'x')` 不漏不误）。dict 形与“写”语义完全解耦 → 读方向 param dict `{'path': CFG}` 构造也 block（R4-3） |
| N-6 rsync/robocopy | **部分修** | rsync 末位=目标语义正确（TC-R3-13/14）。robocopy 名义并入但“末位=目标”与真实语法 `robocopy src dst [files]` 冲突：缴械场景 `robocopy src <home> config.yaml` **PASS 放行**（探针 P2）；_verify_r3.py:67 自测即记录该 PASS，但未入 test 回归、未入边界登记（R4-5）。rsync `-t`=preserve-times 被 cp 专属 `-t` 目标分支误拦（R4-1） |

## 二、新代码面审查

1. workdir/cwd 双键：OK（理由见上表 C-1）。
2. from-import 门：误拦面=零（保守门设计成立）；漏拦面=别名/换行形态（R4-2）。
   附带：门扫描不剔除字符串/注释文本——`msg="…from subprocess import run…"` 会开
   裸词扫（后果多为放行方向，保守面可接受，建议注释声明）。
3. 三引号折叠：入口位置正确（判定链最前端，覆盖 os.system/subprocess 递归与全部
   写正则）；混排 `'''"…'''` 折叠后仍可被 terminal 面 _STR_LIT 类正则处理；唯一
   系统性新面 = 文档文本升格为可触发代码（R4-3/R4-4c）。
4. rsync 并入后 cp 分支读方向：负例仅锁定裸 rsync（TC-R3-14）；带 `-t` 即误拦
   （R4-1）——同函数 `_terminal_position_is_write` 内 `-t` 分支（L624-628）位于
   命令词无关路径，属复制族扩展时的语义照搬残留。
5. 目录形态判定：末位目录 + home 前缀双条件收紧合理；`norm==home` 与目录目标两条
   收集路径（L768-771）无交集缺陷；未见边界洞。

## 三、降级边界登记核对（CHANGELOG round3 节）

| 项 | 登记 | 理由成立性 |
|---|---|---|
| spawn-exec argv 族 | ✅ L29-30 + handler L287-289 双处 | **成立**。探针 P7：单参捕获只会取首参（程序名）形成假覆盖，os.spawnl→PASS、同语义 os.system→approve 证实“半匹配不如不匹配”；正确判定需 argv 语义解析，与“不加复杂度”一致 |
| tar/unzip/patch/ln/find（=N-8 束） | ✅ L31 一行 | 方向成立（目标位含选项语义/属链接改名族），但**理由仅半句**：未写明效果链（如 `tar -xzf b.tgz -C <home> member` 的落点绕过、ln/patch 与 L4「改名不拦」用户决策同源）。建议扩一句（登记完整性问题，非重开威胁） |
| N-7 exec/eval 套壳 | ✅ L32 | 成立。且字面量内嵌 `exec("open(CFG,'w')")` 实际已被文本级正则覆盖（同 TC-A-25 原理），登记的“不修”仅指共现启发式——边界自洽 |
| tool_call 泛化分发 | ✅ L33-34 | 成立（归变量拼接声明边界，与 Q-03 一致） |
| M-3 会话级 cd 跟踪 | ✅ L35-37 | 成立且**本轮独立实证**其前提：execute_code schema 仅 code/reset（code_execution_tool.py L882-892），sa-0 该项坐标确不成立。缺口：平台 `_resolve_command_cwd` 还有 session-cwd 记录回退（terminal_tool.py L770-797），handler 回退进程 os.getcwd() 的第二级落差未在 M-3 或 LOW-3 显式登记（R4-6，LOW） |

## 四、新 findings

- **R4-1（MEDIUM）** handler.py L622-628：`-t` 目标分支不判命令词。
  `rsync -t <CFG> backup/`（读方向）→ approve 误拦（探针 P1 实证；rsync -a 对照放行）。
  同族根因即 R4-5：复制族扩展时把 cp 专属选项语义照搬到全族。
  修法：`-t` 分支前加 `cmd in ("cp", "copy", "install")` 门（rsync/robocopy 只走末位分支）。
- **R4-2（MEDIUM）** N-1 from-import 门两个同类逃逸（探针 P3 实证均 PASS 放行）：
  a) `from subprocess import run as r` + `r('echo x > CFG', shell=True)`——正则只认裸词；
  b) 括号多行 import（`import (\n run,\n)`）——`[^\n#]*` 限制跨不了行。
  修法：捕获 `as` 别名进扫描集；`import` 体允许跨括号（`[^#\n]*(?:\([^)]*\))?[^)]*\)` 一类）；
  补两条回归（正例 block + 别名负例不误扩）。
- **R4-5（MEDIUM·覆盖声明缺口）** robocopy 并入 _COPY_CMDS 但末位启发式对 robocopy
  失效：`robocopy src <home> config.yaml` 写方向放行（探针 P2）。_verify_r3.py:67
  已记录该 PASS 但既无 TC 锁定也无 CHANGELOG 边界条目（与 C-1“测试打在假坐标”同类：
  声明与实效分叉）。三选一：dst 第 2 位专用分支 / 移出 _COPY_CMDS 并入 tar 行登记 /
  至少把该场景落 TC 并在边界声明写明。
- **R4-3（LOW）** N-5 dict 形与读写语义解耦：execute_code 构造 read_file/任意工具
  参数 dict `{'path': CFG}` → block（探针 P4）。与 docstring 假阳性（P5）同属静态文本
  启发式的固有保守面，但本轮新代码面集中显形。修法（择一）：dict 分支要求同行
  共现写语义 token（content/new_string）；或 handler 注释 + CHANGELOG 写明该接受误拦面。
- **R4-4（LOW·工程质量腐化残留）**
  a) `_SUBPROC_BARE_RE_TMPL`（L295）死常量——AST 扫描实证模块级定义零引用（R-8 同类，
     同族清理不彻底：实现改用了循环内联 compile）；
  b) L826-838 双层缩进漂移（for 体多缩进一层，恰落在 round3 新代码段内，S-1 格式纪律回潮）；
  c) 三引号折叠 `"""→"` 无损归一未做（现折成同字符 `"""→"""→"` 可再省一步引号配对扰动）。
- **R4-6（LOW·登记完整性）** M-3 未覆盖 terminal session-cwd 记录回退落差（见三节表）；
  tar/N-8 行理由仅半句（见三节表）。

## 结论

**CHANGES REQUIRED**

阻断：R4-1、R4-2、R4-5（修复或按规范登记边界 + 回归锁定，二者均可闭）。
非阻断随修：R4-3、R4-4、R4-6。
round3 六项中 C-1/N-4/H-1 验收通过，N-1/N-5 完整、N-3 达标带新保守面，N-6 部分修。
声明边界主体（spawn-exec/N-7/M-3）登记与理由经得起复核；tar 行与 M-3 需按 R4-6 补全。
