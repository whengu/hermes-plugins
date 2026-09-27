# write-guard round6 质量复审报告（只读，2026-09-22）

| 项 | 值 |
|---|---|
| 被审对象 | git 8fa3fe1；工作区=HEAD（`git status --short` 干净）；部署三方一致性实证：workspace / .hermes/plugins/write-guard / profiles/{architect,developer} 镜像 ×3 文件 sha256 **全 SAME**（handler `b8f1217a…`），镜像目录零 .tmp/零 pycache 残留 |
| 方法 | 实跑 test_handler.py（**ALL PASS 29+4+219 属实**）、_verify_r5（28/0）、_verify_r3（25/0 无回潮）；AST 复扫（compile OK、死常量 0、未用顶层名 0）；新增定向实测 ~35 探针 + deploy.mirror_to_profiles 四场景沙箱实测（workspace 内临时目录，已清理） |
| 纪律 | 不采信自述，逐条以原始场景重跑；只读被审文件 |

---

## 一、round6 修复项逐项验收

| 项 | 判定 | 证据 |
|---|---|---|
| **D1**（镜像反缴械） | **已修** | TC-R6-01~04 全绿；镜像目录 write_file/patch→block、cp 无斜杠→approve、cat→放行；扩面核查：profile 下**非** write-guard 插件文件（plugins/some-tool/handler.py）write_file=零扩面 ✅；段边界核查：`write-guard-old` 不被 _GUARD_DIR_SEG_RE 命中（需 `/` 或行尾）✅——其被拦系 C4 末位泛化，非守卫段误伤。 |
| **C3**（--target-directory/-t 簇） | **不完整** | 长形空格/= 粘连/词尾全拦（实测含词尾形 approve）；短形簇 -rt approve；`cp -T` 不误扩（负例放行；`cp -T evil <guard>/handler.py` 拦是末位目标语义，与 -T 无关，正确）。**残余缺口**：GNU 合法粘连短形 `cp -t<dir> evil` 放行——含缴械场景 `cp -tD:/…/plugins/write-guard evil`→None（分支要求 t 后空白/行尾；且该 token 非末位，C4 收集面不兜）。另注释声称"与 -t= 粘连形"实测同样不命中（`cp -t=<dir>`→None）——**注释与实现矛盾**。此与 F-1/H-1"合法省/粘形态即绕过"同根，登记未覆盖 → 新 finding **Q-6-1（MED）**。 |
| **C4**（末位 home 内无斜杠） | **已修（微扩）** | cp 末位 home 内目录无斜杠→approve；mv/cat 负例放行（名实一致）；home 树外末位不扩。微扩：实现收集的是 home 内**任意末位 token（含普通文件）**，`cp a.txt <home>/readme-notes.txt` 亦 approve——注释只说"目录"，假阳性面轻微（approve 非 block，保守方向）→ 并入 Q-6-3。 |
| **F-Q1**（robocopy 名实） | **已修** | handler L567-569 与 CHANGELOG 均改为"零兜底声明边界"；实测 robocopy 写 config/缴械 handler 均放行——**与"零覆盖"登记名实一致** ✅；TC-R5-15 锁 PASS 保持。 |
| **F-Q2**（镜像原子换入） | **已修** | 沙箱四场景实测：A 正常镜像哈希一致、目标目录零 .tmp；B 目标位被目录占（os.replace WinError 5）→ 受控 `FAIL … 镜像异常` 输出、**无"已镜像"误报**、返回 None→main 1、无裸 traceback；C 故障修复后重跑成功（.tmp 被幂等覆盖）；D 源文件缺失→受控 FAIL 不外抛。残余微疵：B 失败时 `handler.py.tmp` 残留不清理、且 __init__ 已换入 handler 失败=profile 级混合版本窗口（docstring"不留半写"严格仅文件级成立）→ Q-6-4。 |
| **F-Q4**（getstatusoutput） | **已修** | `subprocess.getstatusoutput('echo x>CFG')` block；star 裸形、`sp.` 别名形同拦；与 _SUBPROC_FUNCS 名单两处同步无漂移。 |
| **微疵三条** | **已修** | F-2 恒死支删除（L1001 单表达式实证）；L553 陈旧注释已拆（rsync 句与 robocopy 句不再"先陈旧再自否"）；TC-E70 标题改"幻觉 cwd=F-6 防御纵深超集"，与实测语义相符。 |

## 二、round5 遗留三项处置质量

- **F-Q1 改写**：名实一致 ✅（见上，登记句承诺已消除）。
- **F-Q2 失败路径**：实测原子换入成立、失败不外抛不误报 ✅；仅 .tmp 残留/混合版本两条 LOW 残余。
- **F-Q6 三小项**：① TC-E70 改名 ✅（假坐标用例转为"幻觉参数防御纵深"正名，语义诚实；TC-E71 标题仍留"C-cwd 负例"字样未随改——微疵并入 Q-6-4）；② R4-3 dict 形"按写处置=保守方向"已补登 CHANGELOG L44 ✅；③ tar 行理由扩写已补（L45-46"与改名族同源不扩"）✅，实测 tar -C/ln -sf/unzip -d 放行与登记一致。

## 三、登记边界条目 vs 实测

| 条目 | 实测 | 一致 |
|---|---|---|
| F-Q3 star-import 覆写 | `from subprocess import *` 后用户 `def run()` 携写参 → block（fail-closed 方向） | ✅ |
| F-Q5 ~/xcopy 跨家 | `xcopy evil D:\…\.hermes\config.yaml` 等 → 放行（本机 ~ 与 home 异根、单根归一化设计后果） | ✅ |
| M-3 会话 cd | 单命令内 `cd <home> && echo>config.yaml` → block；跨调用无状态=登记语义 | ✅ |
| robocopy / tar / ln / N-7 | 全放行，与"零兜底/声明边界"登记逐字对应 | ✅ |
| **CHANGELOG 与实效分叉核查** | round6 各登记句实测均兑现；唯二微漂移=Q-6-1 注释"粘连形"虚假声称、C4"目录"实为任意末位 token——均 LOW 级，未再现 F-Q1 型虚假承诺 | ✅（带 LOW 尾巴） |

## 四、同类腐化残留 + 新 finding

AST/正则/文本扫描：compile 通过；顶层死常量 0；但——

| # | 级别 | 内容 |
|---|---|---|
| **Q-6-1** | **MED（C3 同族缺口）** | `cp -t<dir>`（GNU 合法粘连短形）旁路，缴械场景 `cp -t<guard> evil` 实测放行；`-t=` 粘连亦不命中而注释声称覆盖（注释与实现矛盾）。建议：`-[a-zA-Z]*t(?![a-zA-Z])` 改为后随 `(?=[\s=]|$)` 之外再接路径形（如 `-[a-zA-Z]*t(?![\w-])` + 粘连提取），或至少改正注释+CHANGELOG 登记残余。TC 补 2 条。 |
| Q-6-2 | LOW（死支复发） | `_is_guard_dir_target` L622-623 第二分支实测**恒不可达**（branch1 的 home 前缀+段匹配完全覆盖主目录形；逐候选验证 b2且非b1=∅）——round5 F-2 刚删过恒死支，本轮泛化时又引入同型腐化。删支或注释说明保留理由。 |
| Q-6-3 | LOW（风格/名实微漂） | L475 为 round6 新增 161 字符单行、中间以连续空格粘连两条件（缩进/换行风格漂移）；C4 注释"home 内**目录**"而实现收任意末位 token（含普通文件，approve 假阳性面微扩，保守方向）。 |
| Q-6-4 | LOW（部署/测试尾巴） | mirror 失败残留 `.tmp` 不清理（重跑幂等，无害留污）；docstring"不留半写"严格仅文件级、profile 级混合版本未声明；TC-E71 标题未随 E70 改名同步；"write-guard"/"plugins" 字面量 2-3 处未收敛单一来源。 |

正面确认：round5 全部封堵场景重放无回潮（28/0、25/0）；D1/C4/F-Q2/F-Q4 修复未破坏既有矩阵（TC-R5/R6 全绿、管道/cd/内嵌链行为不变）；测试计数 11 条 TC-R6 与 commit message 相符。

## 五、裁决

**CHANGES REQUIRED（轻量）**——round6 七项中六项验收通过、F-Q2 失败路径四场景实测真到位、profile 镜像磁盘逐字节一致；唯一实质缺口 **Q-6-1**（C3 未封 -t 粘连短形=同族绕过仍开，且注释虚假声称覆盖）；Q-6-2/3/4 为一行级随修与登记尾巴。无行为回潮、无 F-Q1 级虚假登记复现。

*方法注：本审计的镜像失败路径实测在 workspace 沙箱目录完成（tempfile 被自家守卫 C 当场拦截，改道 workspace——顺带实证 C 守卫对真实会话生效），沙箱已清理，全程未触碰被审文件与部署目录。*
