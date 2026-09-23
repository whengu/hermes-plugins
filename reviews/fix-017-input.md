# fix-017 修复规格（round17：F-16-S1 宽拦族 tilde 封堵 + cp 宽拦文案自解释归正 + NOTES）

基线：git（round16 闭环 70948f8 后复审档案批），代码面 = 70948f8 态，
handler sha[:16]=9295bf170ecb399d，test 29+4+381 ALL PASS。
准绳：requirements/requirement-20260922-boundary.md（纳入第 6/7 条同语义必防）+
用户裁决 A（decision-20260923-cp-skills-explain.md：宽拦维持、但必须"可解释"）。

## 立项依据（三方独立证据）
1. round16 合并终审 F-16-S1（MED）：`_protect_view_norm` 只接了"受保护清单判定"，
   **HOME 级宽拦族**（cp 目标=HOME 内任意落位，非清单文件：x.dat、skills/、logs/、
   HOME 本身、无尾斜杠目录）的 tilde/$HOME/别名形双代同漏——而 round16 已把 mv
   第二跳焊住（别名 mv 目标→approve），**cp 入口跳 tilde 全开 = cp+mv 两跳链复活**，
   恰破用户裁决 A 的立论前提。
2. PM 独立复验：8 靶心基线全 PASS（含 `-t` 粘连/分列、bash -c 载体内）；猴补丁定演
   （_normalize_path 出口套视图，签名保留 base kw）7/8 缺口转 approve、9 锁零误拦、
   绝对形零漂移。
3. 同批：用户可解释性要求——宽拦场景审批卡谎称"写入受保护的 Hermes 配置文件"
   （M1 断言基线 FAIL 坐实文案失实）。

## 改动1（行为，净 ~5 行，零新逻辑）
宽拦判定/收集链各比较点的 `norm` 换 `_protect_view_norm(norm)` 视图比对（与 round16
1b/1c 完全同构；F-7-2：判定视图专用，token 化/分发 norm 链不动）。PM 实核比较点清单
（handler 70948f8 行号，grep 复核为准）：
- L798 H-1 尾分隔目录支 `norm.startswith(_hermes_home()+_SEP)`
- L807-813 F-A7/-t 支 `home=...` 后 `norm == home or norm.startswith(home+_SEP)`
- L726 `_is_guard_dir_target`（round16 已接——**勿重复接**，先读现状）
- L1054-1065 收集位点 is_dir_target 两个比较 + C4 末位支
- （T6 `-t` 粘连 / T8 分列 经上述后自然命中——PM 定演 `-t` 粘连在视图出口法下 1 形
  未转，系该支比较点未全覆盖；施工时以 pm_verify_017 T6 转绿为准补点，禁改语义）
**施工纪律**：以 pm_verify_017 全绿为准找齐接点，禁一把梭改 _normalize_path 出口
（影响面不可控）；逐点接、每点跑一次断言。

## 改动2（文案自解释，行为零变化）
`_config_write_disposition`/approve 消息分两支：
- 清单面真配置（yaml/json/config/.env/plugins 代码）→ 保持现「受保护的 Hermes 配置
  文件」模板（M2 锁）；
- **宽拦族**（HOME 内非清单落位）→ 新模板：「write-guard 落位审批：工具「X」将向
  Hermes 目录（.hermes）内 {path} 落位文件。该通道防 cp+mv 两跳改写配置（读、改名、
  源位不受限），经您批准后继续。」（M1 锁含"两跳/落位"且不再谎称配置文件）
实现提示：`_is_protected_config(norm)` 为宽拦分流谓词（已有返回值处不重算）。

## 改动3（NOTES 随批，全部实测背书）
1. review-016 NOTES 三条：alias/绝对 mv 语义分歧点名入 CHANGELOG 接受边界节；
   fix-016.md 纪律框勾齐；「12 行」口径补句（实际 +30/-1）。
2. CHANGELOG round17 节 + round16 节「全族判定继承」失实句改实（F-16-S1 根因句，
   名实现象第七次登记）。
3. TC-R17 ≥12 条（8 靶心 + 读/源/改名 4 锁 + 文案 M1/M2 双断言）。

## 完成定义（PM 门禁复跑）
1. pm_verify_017 → **0 失败**（19 形；基线 9 FAIL 全转绿、10 ok 零回退）
2. pm_verify_016 16/16、pm014 29、pm013 30、_verify_r14 43、九 verify、pm012 零 FAIL
3. test_handler ALL PASS（381+≥12）+ 红线四形 4/4
4. 两跳链端到端反例复验：`cp evil ~/.hermes/x.dat`(hit) 且 `mv <H>/x.dat <CFG>` 绝对
   改名形维持红线 PASS（链已断在入口，不扩 mv 面）
5. 文案 M1/M2 双锁

## 纪律
制品 reviews/fix-017.md 骨架第一步落盘每步 [DONE]；≤10 分钟探针照图施工；CHANGELOG
数字先实跑；py_compile 先行；不改 deploy.py/plugin.yaml；不 commit 不 deploy；
终答 ≤150 字只给 pm017 末行+test 末行+verify 数组+文件清单。
