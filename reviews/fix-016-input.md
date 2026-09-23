# fix-016 修复规格（round16：`.hermes` 段锚定归一——tilde/$HOME/别名路径写旁路封堵）

基线：git ab33024（round15 收敛态，handler sha[:16]=149497733ab9e8c2，test 29+4+369 ALL PASS）。
需求来源：用户 2026-09-23 提议「配置文件修改审批要加 ~/.hermes/ 路径检查，干脆用
*/.hermes/*.yaml」+ PM 实测坐实为纳入范围真旁路（写入位判定只认展开后的真实绝对路径）。

## 旁路实测（当前 handler，PM execute_code judge 背书）
- `cp evil ~/.hermes/config.yaml` → **PASS**（绝对路径同语义=approve）
- `echo x > ~/.hermes/config.yaml` → **PASS**（重定向写位）
- `sed -i 's/a/b/' ~/.hermes/plugins/write-guard/handler.py` → **PASS**（tilde 形缴械）
- `tee $HOME/.hermes/auth.json` → **PASS**
环境事实（用户记忆档案）：git-bash `~/.hermes` 经符号链接可达线上配置目录——tilde 形
不是「打不到保护面」的假旁路，是真写威胁。

## 修法（设计决策：段锚定归一，不采用裸 glob 字面匹配）
裸 `*/.hermes/*.yaml` 的问题：字符串出现即弹 → 把 `cat ~/.hermes/config.yaml`（读位）
也弹卡，违背"读不拦、写才弹"与零误拦优先；且漏 plugins/*.py、memories 面。
正确做法：**写目标判定输入处，对 norm 后路径做 `.hermes` 段锚定归一**：
1. 检测路径含独立段 `.hermes`（段边界=前导 `^|/|\\`，`.hermes-agent` 等前缀名**不算**）；
2. 取其后的相对部分 rel，替换前缀为真实 `HERMES_HOME`（即 D:\myagent\.hermes），
   得到等价绝对路径后**进入既有受保护面判定管线**（config.yaml/plugins/*.py/memories 等
   既有集合自动全覆盖，读写位置语义、-t/of=/cluster 全族判定继承，不新增判定逻辑）。
3. `$HOME`/`${HOME}`/`%USERPROFILE%` 前缀先按现有 norm 展开或等价归一（tilde 面已靠 2
   覆盖的话不强求，形进 TC 锁）。
预期体量 ≤12 行，单一插入点（写目标判定输入，token 化/norm 链语义不动——F-7-2 纪律：
归一只发生在"保护面匹配视图"，不改动分发用的 norm）。

## 靶心（当前 PASS，修后必 hit；pm_verify_016 断言）
- T1 `cp evil ~/.hermes/config.yaml` → approve
- T2 `echo x > ~/.hermes/config.yaml` → block（重定向）
- T3 `sed -i 's/a/b/' ~/.hermes/plugins/write-guard/handler.py` → block（缴械）
- T4 `cp "-t~/.hermes/plugins/write-guard" x` → hit（tilde×cluster 组合）
- T5 `curl "-o~/.hermes/config.yaml" url` → hit（tilde×粘连值组合）
- T6 `tee $HOME/.hermes/config.yaml` → hit
- T7 `cp evil %USERPROFILE%\.hermes\config.yaml`（cmd 载体）→ hit（如载体不支持则降登记）
- T8 绝对路径旧别名 `cp evil C:/Users/guwh/.hermes/config.yaml` → approve（符号链接别名面）

## 锁形（修后不得回退/不得误拦）
- K1 `cat ~/.hermes/config.yaml` = PASS（读位不拦——本修法最关键的反例）
- K2 `mv ~/.hermes/config.yaml x` = PASS（rename 源位读，红线）
- K3 `mv x ~/.hermes/config.yaml` = approve（目标覆写）
- K4 `cp evil ~/.hermes-agent/config.yaml` = PASS（`.hermes-agent` 非 `.hermes` 段）
- K5 `echo x > ~/.vscode/settings.json` = PASS（非 .hermes 零扰动）
- K6 `cp evil <D:\myagent\.hermes\config.yaml 绝对形>` = approve（绝对形不回潮）
- K7 `cat C:/Users/guwh/.hermes/config.yaml` = PASS（别名读位不拦）
- 全量零回退：pm_verify_014 29/0、pm_verify_013 30/0、_verify_r14 43/0、九 verify、
  pm_verify_012、红线四形（gateway=block/cp 配置=approve/Copy-Item 源读=PASS/
  -Destination CFG WS=approve）、test_handler 全绿（TC-R16 ≥10 条含上述正反）。

## 交付纪律
制品 reviews/fix-016.md 骨架第一步落盘每步 [DONE]；探针 ≤10 分钟；照图施工禁再设计；
CHANGELOG round16 节每个数字先实跑；不 commit 不 deploy；不改 deploy.py/plugin.yaml。
