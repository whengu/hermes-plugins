# round11 质量路终审探针（audit-round11-qual）

四件，全部走 on_pre_tool_call 正确入口（round10-context §入口口径遵守）：

- r11q_collateral.py —— 任务③独立回归 27 例现行为断言（cp/copy/install/rsync/robocopy/
  sort/curl/sed/mv/tee 族 × -t 支交叉 × PS named 交叉 × 未知命令 -o × 载体组合）。
- r11q_diff.py —— 27 列 r10 基线（handler_r10commit.py，git 2cc28cf 权威快照）新旧差分：
  仅 5 例变化，全部 = fix-011 §0 预期翻转（m/o/p/q/r + 载体双向 i/k），其余逐一同向
  → 末位启发否决连带面零意外变化。
- r11q_diff9.py —— 13 例对 r9 代际（handler_r9_cbd6301.py）差分：2 例变化 = F-9-1
  复制族摘出预期向（Copy-Item 源位 r9 block→r11 PASS，round10 §0 联动翻转登记同款），
  非 round11 新引入。
- r11q_susp.py —— Q-1 新发现实锤：`Copy-Item -Path/-LiteralPath <CFG> <非保护末位>`
  r10=PASS → r11=approve（PS 语义 -Path 是源位，被 TARGET 支判写）。含对照形：
  双标志 -Path CFG -Destination 非保护 = PASS（末位启发否决兜住，反证 TARGET 判定冗余）。
- r11q_sha.py —— 部署三处镜像（源/主部署/profiles{architect,developer}）× 三文件
  sha256[:16] 一致性核对（本轮实跑 BAD=[]）。
