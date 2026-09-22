# fix-014 修复规格（round14：粘连目标选项引号整包族封堵 = sec F-13-S1 + qual Q13-A/B 合并）

基线：git a927010（代码面 = 10a2094 态，handler sha256 前16=cf61f3291970a021，347 用例
ALL PASS）。准绳：requirements/requirement-20260922-boundary.md（本批全属**纳入范围**：
整词引号包一个完整 token + 常规粘连，非劈 token 排除族）。

## 立项依据（两路独立复现 + PM 第三路复验，全部端活证）
- sec F-13-S1（HIGH，=PM X-14-1 同洞）：`-t`/`--target-directory=`/`dd of=`/`install -t`
  粘连支引号整包形成体系漏拦，bash 活证真写，含守卫缴械形 `cp x "-t<守卫目录>"`。
- qual Q13-A（LOW~MED）：引号包 cluster 选项词+**空格分离值** `curl "-so" <CFG>` /
  `"-sSo"` / wget `"-qO"` / sort `"-ro"`，curl 活证 rc=0 实写；裸形均 block（唯一切换量=引号）。
- qual Q13-B（LOW）：`cp "-tdst"` 粘连 cluster 引号包，cp 活证真写。
- PM 复验：pm_verify_014 基线 **13 靶心 FAIL / 16 ok**（reviews/fix014-scratch/）。
- 三代既有（94998f5/4e254c8/10a2094 同 PASS），**非 round13 引入**——系 r13 改动B 只接
  `_GLUED_O_RE` 匹配输入、同族邻支未接（覆盖不对称教训实锤）。

## 改动A（主修，与 r13 改动B 严格同法同纪律）：粘连入口全族接 `_pair_unquote`
以下**匹配输入**各接 `_pair_unquote` 一处（仅判定视图；token 化/norm 链不经过——F-7-2
禁令不回潮；均在复制/输出/写目标命令门后，零扰动门外）：
1. `_GLUED_T_RE`（`-t<dir>` 粘连，cp/install/robocopy 族门后）
2. `--target-directory=` 前缀支（startswith 锚 → 先剥再判）
3. `of=` 前缀支（dd 写目标）
4. `_OUTPUT_FLAG_EQ_RE` 长形 `--output=` 支（curl 死选项，剥后 block=无害多防，比照 r13
   `-o=` 附录句，CHANGELOG 登记一句）
预期翻转：T1~T7、T15、T17（pm_verify_014）→ hit。锁形 K1~K5、K7~K8、T16、K10 不回退。

## 改动B：`_OUTPUT_QUOTED_RE` 内容段并 cluster 尾 o 支
现内容段限「仅选项词」（单 o/O 约束不回退）；扩为并一个支：引号内 = cluster 字母串且
**尾字母 o/O**（形如 `["'][-]?[a-zA-Z]*[oO]["']`，比照 `_OUTPUT_FLAG_RE` dash cluster
支同款字符类，双 dash 与 `-O` 大写红线语义不扩），值走既有后随 token 判定。
预期翻转：T11~T14 → hit。必测负例（零误拦锁）：T18 `curl "-oL"`、K9/K11 `grep "-o"/"-so"`
门外、`"-H"` 任意引号词、URL 整词含 o。

## 改动C（NOTES 随批，全部实测背书）
1. **Q13-C 补账**：回填 reviews/fix-013.md §A/§B/§N/§V（权威来源=CHANGELOG round13 节 +
   git diff 10a2094 + pm_verify_013 实跑值；Z2 行「修后预期」回填终值 PASS 注「绑定错误零写
   语义正确」）——上位两文档失实句 PM 已改实，勿再回潮。
2. **Q13-D 口径句**：CHANGELOG round13 节补一句调和「第 3 次（词表全局化类同构）/第 5 次
   （review-012 全量规律口径）」分母；r9 S-2→F-9-1 显式判定不计入词表类（出现即写≠收窄）。
3. **Q13-E 注释**：handler.py L281 邻域注释引用已删符号 `_GLUED_NAMED_RE` → 实名
   `_PS_GLUED_NAMED_RES`。
4. **教训固化句**（入 CHANGELOG round14）：引号剥离类修复，验收面必须扫**全族粘连入口**
   （-o / -t / --target-dir / of= / 冒号形 / cluster+空格值），逐分支翻转表+逐分支活证。

## 完成定义（PM 门禁复跑清单）
1. `python reviews/fix014-scratch/pm_verify_014.py` → **0 失败**（29 形）
2. `python test_handler.py` → ALL PASS + TC-R14 ≥14 条（改动A/B 正反两面各锁）
3. `python reviews/fix013-scratch/pm_verify_013.py` → 30/0 不回潮
4. `_verify_r13/r12/r11/r10/r9/r8/r7/r5/r3` → 全零失败
5. `python reviews/fix012-scratch/pm_verify_012.py` → 零回退
6. 红线四形（on_pre_tool_call 入口）：gateway=block、cp 配置=approve、Copy-Item 源位读=PASS、
   `-Destination CFG WS`=approve；引号整包非保护目录=PASS（零误拦）
7. 端活证抽查：改动A 至少 2 形真写复核（bash cp -t 落盘 / dd of= 覆写）+ 负例不误执行
