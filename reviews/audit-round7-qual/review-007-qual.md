# review-007-qual — write-guard round7 质量复审（只读，基线 git 90de321）

日期：2026-09-22；复审人：sa-1 qual。探针：r7_q_probe.py / r7_q_ast.py / r7_q_deploy.py / r7_q_f1.py（载荷全落盘，命令行零载荷）。

## 0. 基线实跑（不采信自述）
- `test_handler.py`：**ALL PASS 29+4+233**（含 TC-R7-01~14）✅
- `_verify_r7.py` 30/0、`_verify_r5.py` 28/0、`_verify_r3.py` 25/0 ✅（与 round7-context 宣称一致）
- 部署一致性：git 90de321:handler.py vs 主部署 `D:/myagent/.hermes/plugins/write-guard/handler.py` 及 architect/developer 双镜像——**行尾归一后逐行相同**（字节级仅 CRLF 差异，deploy.py 落盘行尾，无碍）✅
- AST 可解析；`guard_dir =` 字面量残留=0（Q-6-2 单源确认）；`>100` 长行残存 L525(113)/L535(110) 两处。

## 1. 逐项验收
### NL 分段 —— **不完整**
D 卷 9 形实跑全封堵（换行 cp 主guard/镜像/config、CRLF、truncate、install、rsync、--tdir、-t、续行），读/workspace 写/无关命令负例零回潮 ✅。
但归一 `command.replace("\\\n"," ").replace("\\\r\n"," ")` 对 **反斜杠+反斜杠+LF（`echo a\\`↵`cp evil <guard>`）**失手：把「字面反斜杠收尾 + 真命令分隔」错当续行粘连成一行，第二行缴械 cp 变成 echo 的参数 → **整条放行**（P-A1/A2/A4、X2/X5 实测 PASS）。真实 bash 中 `\\` 是字面量、LF 仍分段，cp 实际执行=反缴械旁路，**与 round7 主题修复同形同类，HIGH 级**。
`\<CR><LF>` 单形（X1）粘连后成为合法 echo 参数（P-A1b 对照组证实粘连语义本身正确，非缺陷）。`\`+裸CR（P-A5）落入保守 approve 方向，可接受但未声明。`_guard_gateway_cmd` L1076 同根单形归一（D 守卫防呆定位已登记，降为附带项）。
修法方向：粘连前先占位替换 `\\\\`（偶数反斜杠），或按「`\n` 前连续反斜杠个数奇偶」判定；TC 补 `\\`+LF/`\\`+CRLF 两攻击形。
CHANGELOG「D 卷全 9 攻击形封堵」对 `\\` 形不成立 → 登记与实效分叉。

### Q-6-1 —— **基本已修，组合缺口一条（F-7-2）**
- `_GLUED_T_RE`：未知命令门挡实测（tar/ls 粘连 PASS 不误伤，P-C4/C5）✅；`-tstage` 贪婪回退=末位 t 切分，与 getopt `-s -t <rest>` 语义实测一致（P-C1/C2）✅；`-tr` 歧义负例维持 ✅；`-t=<dir>` ✅；`install -t<HOME>` ✅；bash -c 递归面 ✅（_verify_r7）。
- **F-7-2（MED）：引号粘连长形 `cp '--target-directory'=<dir>` / `"--target-directory"=<dir>` 放行**（X3/X4 实测）。GNU 合法形、shell 剥引号后与 C3 裸形同义；token 以引号起始→`startswith("--target-directory=")` 失配，`_COPY_T_QUOTED_RE` 只认「引号-选项-引号」整体后随空格的分离形。Q-6-1 收了粘连短形+引号分离形，**两形的组合**漏收=同类腐化（组合覆盖缺口）。修法：对 raw 先 `_strip_outer_quotes` 式剥「前缀引号选项+引号+等号」再入既有链。
- `_COPY_T_QUOTED_RE` 误命中面（验收重点）：`grep '-t' CFG` 不触发（非 cp 门）✅；文件名中嵌 `'--target-directory'` 文本→token 边界+末位判定挡住（P-D3）✅；残余假阳性=「`cp '-t' <CFG> out/`（'-t' 为文件名、CFG 源位）」→保守弹卡（P-D1 实测 approve，无硬拦、方向保守）。**F-7-3（LOW）**：CHANGELOG 负例只登记 `-tr` 歧义与非 home 两形，此 FP 未登记——补登记边界。

### Q-6-2 —— **已修**
死支删除、字面量收敛单源（残留计数=0）；L681-683 `or _is_guard_dir_target(norm)` 非冗余（镜像可在其它 root 下）；调用点三处行为实测：guard 无斜杠 cp=approve、guard 子目录 approve、`write-guard-old` 段边界不误伤（读位 PASS/末位=既有 C4 泛化保守 approve，_verify_r7 已如实标注「非段误伤」）、write_file old 目录=PASS（P-E1 实测，我预期误设不影响结论——段边界真负例由 P-E1 修正期望为 PASS 实测通过）；回归 R7-13/14 + r5/r3 全绿 ✅。

### Q-6-3 —— **不完整（微）**
原 161 字符粘连长行已规范多行 ✅；C4 注释「任意末位 token 含文件=保守方向」名实相符（P-E2/C4 实测=保守 approve）✅。**但 L525/L535 两处 110~113 字符长行**若规范阈值为 100 则同类残留未清、若 120 则合规——阈值依据在 design/quality-plan 中未检索到明文 → **F-7-4（OBS）**：请在 CHANGELOG 或规范中写死行长阈值，并处理或豁免该行。

### Q-6-4 —— **已修**
`.tmp` 幂等暂存+失败现场不自动清理：docstring 声明核查通过；TC-E71 标题「C-cwd 负例」语义仍为放行方向负例、CHANGELOG「名实无分叉不改」的论证与实际一致 ✅。

## 2. 登记边界条目核对（实测）
robocopy 三参=PASS（零兜底登记真实）✅；tar -C=PASS ✅；os.spawnv argv=PASS ✅；F-Q3/F-Q5(~/xcopy)/M-3/N-7/N-8 沿用前轮证据不重跑；F-Q6 dict 形保守方向维持 ✅。
**分叉点**：①「D 卷全 9 形封堵」未覆盖 `\\`+NL（F-7-1）；②「零回潮」结论对组合形 `'--target-directory'=` 未成立（F-7-2）。

## 3. 发现清单
- **F-7-1（HIGH，round7 修复自引入同形残面）**：`\\`+LF（及 `\\`+CRLF）被续行粘连错并，第二行缴械命令降为参数→放行；gateway 守卫同根。
- **F-7-2（MED）**：`cp '--target-directory'=<home>` 引号粘连长形放行（Q-6-1 组合缺口，可缴械）。
- **F-7-3（LOW，登记不全）**：引号选项形 `cp '-t' <CFG> out/` 假阳性弹卡未登记为边界。
- **F-7-4（OBS）**：L525/535 长行残留，行长阈值无明文依据。

## 4. 裁决
**CHANGES REQUIRED**（F-7-1 必修并补 TC；F-7-2 同修或登记边界；F-7-3/4 登记即可）。
