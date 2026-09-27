# fix-018 修复规格（round18：F-17-S1 紧邻前 token 门控收紧——round17 引入误拦回归封堵）

基线：git 1bcc8cd（round17 闭环），handler sha[:16]=0e1e8d4554ac83ff 四点位，
test 29+4+394 ALL PASS。准绳：requirements/decision-20260923-cp-skills-explain.md
（用户裁决 A）+ 读不拦红线 L1（源位读零误拦）。
发现源：round17 终审 F-17-S1（MED）+ PM 独立双代差分复验同证（probe_018_diff.py：
r16 代 4 形 PASS → r17 代 approve，rsync 形两代均 PASS）。

## 根因（第八次名实不实现象：注释承诺「前随」↔ 实现非紧邻 search）
handler.py L1090-1098（1f 补点）：`cp/install` 别名词内，非末位 tilde token 用
`_COPY_T_RE.search(seg[:m.start()])` 判「本 token 处于 -t 目标位」——search 命中段内
**任意位置**的 `-t`，不要求紧邻本 token。`cp -t D:/other/out ~/.hermes/x.dat evil` 的
`~/.hermes/x.dat` 是**源位**（-t 目标已绑定 D:/other/out），却被入收集面→approve。
破红线：源位读不拦。绝对形双代恒 PASS → 同语义异值=误拦向漂移实锤。

## 改动1（唯一代码改动，≤4 行）
1f 分列支判定收紧为**紧邻前一 token** 即 -t 标志：
- 取 `seg[:m.start()]` 尾部的最后一个空白分隔 token（引号内不分隔可用
  `_PATH_TOKEN_RE`/简单 rstrip 切分，以既有工具函数为准，勿新造状态机）；
- 该 token 整词 `_COPY_T_RE` fullmatch（或 rstrip 后 == -t/--target-directory 族）才算
  -t 目标位；粘连形 `_GLUED_T_RE.match` 支不动。
- 同步改注释：删「前随」含糊句，明写「紧邻前一 token」。

## 改动2 验收锁（test_handler TC-R18 ≥8 条 + pm_verify_018 并入主链）
- G1/G3/G6/G7 转 PASS（-t 绑 HOME 外目标 → tilde 源位读）；
- G2/G4/T8 不回退（-t 目标位本身 tilde=hit）；T6 粘连不回退；K1~K8 全不回退；
- 新锁：`cp -t ~/.hermes/out ~/.hermes/x.dat evil`（-t 目标在 HOME 内 + 源也 tilde）
  → 目标位 hit 维持（歧义取拦方向不受本修影响）；
- 双代差分锁：绝对形矩阵 f8465c3 vs 修后全量零漂移（复审亲跑，PM 门禁抽跑）。
完成定义：pm_verify_018 **23/0** + pm_verify_017 19/0 不回退 + test 全链 +
九 verify + pm012~016 全零失败 + 红线四形 + gateway/rm -r 分层不变。

## 改动3 NOTES 随批（round17 终审 4 条）
- N-17-1：fix-017.md §0「引号前缀变体已通」句实测双代 PASS 失实 → 就地改实。
- N-17-2：引号选项词族 `-t "<dir>"` 宽拦面双代对称旁路 → 入接受边界登记
  （boundary 排除口径内：引号劈选项词族，CHANGELOG round18 节明写，不修）。
- N-17-3：rule_key 键 norm 跨别名不互认（round16 既有）→ 登记在册不修。
- N-17-4：无扩展名配置名走落位句 → 在册取舍，CHANGELOG 补一句点名。
- CHANGELOG round18 新节 + **第八次名实登记**（「前随」承诺↔search 实现不符，
  教训句：紧邻语义必须紧邻实现——search 与 match 之差即红线之差）。

## 纪律
- py_compile 先行；不改 deploy.py/plugin.yaml；子代理不 commit 不 deploy。
- 制品 reviews/fix-018.md 第一步建骨架、每步 [DONE] 落盘（10 次截断前科）。
- 端活证若需：workspace 沙箱，严禁触真实 ~/.hermes / D:\myagent\.hermes。
- 探针 ≤10 分钟照图施工，走不通停下报告（禁再设计、禁改 pm_verify_018 断言语义）。
