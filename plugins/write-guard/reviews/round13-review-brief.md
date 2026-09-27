# Round13 双路复审任务书（安全路 sa-0 / 质量路 sa-1 共用）

工作目录 D:\myagent\workspace\write-guard。基线：git HEAD（代码 10a2094 态，handler
sha256 前 16=cf61f3291970a021，主部署+双 profile 镜像一致）；test_handler ALL PASS
（29+4+347）。规格 reviews/fix-013-input.md（含 PM 活证补充节）；制品 reviews/fix-013.md；
CHANGELOG round13 节；准绳 requirements/requirement-20260922-boundary.md。

## 本轮改动（审查面）
- 改动A：`_PS_TARGET_FLAGS` per-cmd 分表（copy-item:{Destination} / tee-object:
  {FilePath|LiteralPath}）+ 派生三表 `_PS_TAIL_ANCHOR_RES`/`_PS_TGT_BIND_RES`/
  `_PS_GLUED_NAMED_RES`（旧全局 `_PS_NAMED_TARGET_RE`/`_GLUED_NAMED_RE` 删除）；
  `_terminal_position_is_write` 命名支三分句重构（判写/判读/无绑定→末位启发），
  否决子句逐 cmd。
- 改动B：`_pair_unquote`（剥成对外层引号一处）仅入 `_GLUED_O_RE` 匹配输入，
  `_OUTPUT_FLAG_CMDS_RE` 门后（curl/wget/sort），token 化/norm 链不经过。

## 硬要求
1. 所有 finding 必须在当前 handler 上**实测复现**（给出复现命令+judge 输出），并附
   **端活证**（pwsh/curl/bash 真实执行证明该形态语义确实写/读目标）——CHANGELOG round13
   固化教训：词表类判定不得只跑翻转表。未活证的主张降为疑问项。
2. 红线：cp/mv/rename 目标位=approve、源位=PASS、Copy-Item 源位读=PASS、
   `-Destination <CFG> <WS>` 真写=approve、rm -r 拦截、gateway restart 拦截。
3. 边界外（变量间接/eval/编码混淆/引号劈 token/奇偶反斜杠）只登记。
4. 特别审：新三分句逻辑的每个分句正反两面；Z1/Z3 双绑 PASS 是否为规则天然导出（无特判）；
   `_pair_unquote` 对非粘连 token（整词被引号包）是否引入新误拦；tee `-FilePath` 引号值
   （`-FilePath "CFG"`）经新 gn 支行为；pwsh 载体递归经 per-cmd 表后 -Command 载荷面。
5. 质量路另核：CHANGELOG round13 节每条声称对拍 git 史与实测（尤其「修复引入回归第 3 次」
   链上两前例的指涉是否属实）；注释与代码一致；行长。
6. 制品纪律：先落盘报告骨架边测边追加 [DONE]，终答 ≤200 字只给裁决+finding 计数。
   报告写 reviews/audit-round13-sec/review-013-sec.md / audit-round13-qual/review-013-qual.md。
7. 不修改被审代码，不 git commit。
