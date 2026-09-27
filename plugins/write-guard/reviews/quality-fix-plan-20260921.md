# write-guard 质量修复计划（依据 sa-1 工程质量审查，2026-09-21）

审查者：deleg_b5774fc6/sa-1（独立只读审查）
结论：功能正确性良好（148 断言实测全绿）；工程质量中等偏弱，系统性欠账 = 过程资产未随决策迭代。
本计划为修复基准；sa-0（对抗安全走查）结果回来后合并第二批。

## 决策项（按最优设计定案，依据用户授权"自己决策"）

| # | Finding | 级别 | 决策 | 修法 |
|---|---|---|---|---|
| 1 | S-1 注释承载决策考古（801 行巨石内嵌 B1~B5/MED/TC-A-62 修订史） | 高 | **修** | 考古全部迁出到 `reviews/CHANGELOG-20260921.md`（新文件）；代码注释只留"为什么"+ 编号引用（如 `# 见 CHANGELOG B5`）。不拆多文件（插件单文件部署现实约束，拆分收益<成本，决策记录在此） |
| 2 | S-2 `_approve_result`/`_config_block_result` 双份 shown 逻辑 | 中 | **修** | 抽 `_shown_path(raw_path, norm)` 公共 helper；两构造函数各自薄封装（返回 shape 不同：approve 带 rule_key，block 不带——语义差异保留，不强行合并成一个） |
| 3 | T 系列：测试 GUARDS[1]/[2]/[3] 硬索引桩替换（守卫 D 插入已引发 6 用例连锁修改） | 中高 | **修** | 新增 `contextmanager _stub_guard(name, fn)` 按 `guard.__name__` 定位索引；所有 try/finally 手搓替换改用它。守卫函数名成为测试契约（重命名即测试失效可见，好） |
| 4 | T-6 不变量测试写成快照相等（_READ_TOOLS == {5项}） | 低 | **修** | 拆成两个独立断言：isdisjoint 安全不变量（红线）+ 清单快照（失败提示"合法新增读取工具需同步改此断言"），互不掩盖 |
| 5 | T-7 hook 用例数魔数 `4` | 低 | **修** | hook 用例收进列表，计数用 len()；同时消掉设计文档 §7.2 "33 条" vs "29+4" 切分漂移（以测试实际结构为准更新文档） |
| 6 | 文档-代码漂移：design.md/requirement 描述 [C,A,B] 顺序与 write_file approve 语义，代码是 [D,C,A,B] + block | 中高 | **修** | design.md 与 requirement-c1.md 更新到 09-21 决策现状（活跃文档就该反映现状）；历史评审记录 reviews/review-001/002 不回改（快照性质），只在其后追加 delta 说明 |
| 7 | R-7 deploy.py 校验自指（copy 后比对刚 copy 的文件）+ 裸 traceback + 路径硬编码 | 低 | **修** | copy 前后双哈希校验（源→部署 hash 相等验证传输无损；copy 前捕获目标旧 hash 报告变更），py_compile 失败 catch 打印友好错误 exit(1)；SRC/DST 支持 argv 覆盖，默认值不变 |
| 8 | R-8 `_expand_env` 两轮魔数、`_normalize_path` 内联正则热路径 | 备注 | **修**（小） | `_ENV_EXPAND_ROUNDS = 2` 命名常量；normalize 内联 `re.match(r"^[A-Za-z]:/"...)` 等预编译为模块级 |
| 9 | P1 实验：`sed -i` 带引号分号形态判定 None（疑似绕过） | 待 sa-0 | **挂起** | 与 sa-0 安全发现合并处置（属绕过面非纯质量问题） |
| 10 | 未用参数 `_terminal_position_is_write(norm)`、`_guard_hermes_config(task_id)` | 低 | **修** | task_id 是守卫统一签名（四守卫同签名，接口一致性优先）→ 保留但在签名注释声明；norm 参数若确未用则删除 |

## 修复顺序
1. handler.py：#2 → #8 → #10 → #1（注释考古外迁，最后做——改动面大）
2. test_handler.py：#3 → #4 → #5
3. deploy.py：#7
4. 文档：#1 CHANGELOG + #6 design/requirement 更新
5. 全量测试 → ty/py_compile → 派独立复审（含 sa-0 findings 合并验证）

## 复审门
修复后派新一轮独立审查（安全 + 质量各一），直到两路 PASS 才算完成。
