# write-guard 审查链终版报告（round2 → round15，收敛达成）

日期：2026-09-23 ｜ 代码基线终态：git `307e5cd`（round15 闭环批；本收线批为纯文档提交，
代码面零差，以 `git log` 实查收线 sha 为准）
handler sha256[:16] = `149497733ab9e8c2`（工作树/主部署/architect/developer 四点位实测全等）
测试面：ALL PASS（29 scan + 4 hook + 369 new = 402 用例）

## 1. 收敛判据与达成状态
判据（2026-09-22 用户边界决策后改写）：**纳入范围内零缺陷 + 排除项全部登记在案 = 收敛**。
- 纳入范围（常规命令/链式/整词引号/常规粘连/内嵌一层）：round15 合并终审 53 形双代差分
  零旁路逃逸、六类粘连入口逐支活证闭环、红线四形+零误拦锁全对 → **零缺陷**。
- 排除项（劈 token 穿插、反斜杠奇偶算术、变量间接/eval/编码混淆、双引号内转义语义差、
  不可运行死形族：curl `-sfo=` / `--output=` / `"-so "`、PS 等号形、Z 组双绑必败、缩写别名
  族、PS 别名 cp/tee、sudo 带值形、N-1 spawn/exec argv）：CHANGELOG 各轮「接受边界/附录
  登记」节点**逐条在册**，N-15-2 补齐最后一项。
- round15 终审计数：HIGH 0 / MED 0 / LOW 0 / 阻断 0；NOTES 2 条已收线（纯文档）。

## 2. 裁决链摘要（14 个审查批）
| 轮 | 安全路 | 质量路 | 修复要点 |
|---|---|---|---|
| r2 | CHG REQ | CHG REQ | workdir 假修复/cp 子目录旁路 |
| r4 | CHG REQ | CHG REQ | H-1 同源再犯等 7+6 条 |
| r5 | (截断写实) | CHG REQ | F-1~7/OBS-1 + F-Q1/Q2 镜像原子化 |
| r6 | (截断写实) | CHG REQ | D1/C3/C4 + cluster/POSIX |
| r7 | — | CHG REQ | 续行归一 F-7-1 |
| r8 | CHG REQ(5) | PASS_WITH_NOTES(5) | S-1~S-5 -o粘连/PS cmdlet/单&分段 |
| r9 | CHG REQ(4) | PASS_WITH_NOTES(2) | 复制族源位归正/载体组合 |
| r10 | CHG REQ(2) | CHG REQ(3) | 命名目标前置/o 短形约束 |
| r11 | CHG REQ(4) | CHG REQ(1) | TARGET 收窄/冒号粘连/引号选项词/cluster 尾 o |
| r12 | CHG REQ(3) | **PASS** | per-cmd 立项（X-13/PM 挖洞合流） |
| r13 | CHG REQ(1) | CHG REQ(2+NOTES3) | per-cmd 目标表+引号粘连+回归教训固化 |
| r14 | CHG REQ(1 MED) | PASS_WITH_NOTES | 粘连入口全族 _pair_unquote |
| r15 合并终审 | **PASS** ✅ | （并入） | 1 字符正则收窄+名实改实 |

修复引入回归 3 次同构（r10→11、r11→12、r12→13）+ 覆盖不对称 1 次（r14 S14-1）——
两条固化教训已入验收纪律：①词表类修复验收必含 per-cmd/端活证；②引号剥离类必扫全族
粘连入口；③正则可选项与注释承诺逐词对拍；④名实不实现象六次后，所有数字/sha/机理句
先实跑再落笔。

## 3. 过程事故如实账
- 子代理终答截断 8 次（round7~14）——制品先落盘纪律后全部挽回核心产物；round15 起全程零截断。
- PM 文档失实声称 6 处（含派单 context 幽灵 sha 0c22eb5、round14 CHANGELOG 机理句）——
  均被独立复审或 PM 自查坐实后同批改实，无一遗留。
- 端活证现场复跑 2 次被 approvals manual 审批卡超时（rm -r 误发被拒 1 次、门禁第 7 项 2 次）
  ——不重试不绕行如实登记，以立项前活证链+复审端活证兜底。

## 4. 遗留（非缺陷，需用户在场）
- **gateway 重启**：PID 17968/16960 自 2026-09-20 运行，round3~15 补丁未在该进程生效。
  `hermes gateway restart` 会被本守卫按设计拦截（红线），重启方式：用户手动执行，或在
  会话内批准审批卡。重启后守卫代际=149497733ab9e8c2 即全量生效。
- 备份件 handler.py.bak-* 在工作区根（git 未跟踪），可由用户处置。
