# round5 复审基线（2026-09-22 10:4x）

被审对象不变（workspace/write-guard 源码 + D:/myagent/.hermes/plugins/write-guard
部署一致性 + 本轮新增：deploy.py 的 profile 镜像通道）。基线：git 4d08ddd，
handler.py 含 round5 全部修复，test ALL PASS 29+4+208。

## round5 修复项（逐项验收）
- F-1：_is_guard_dir_target 三处接入（复制族末位/cp -t/收集面）——cp 守卫目录
  **无尾分隔符**不再旁路。注意处置=approve（复制族走审批卡是用户决策，不是 block）。
- F-2：terminal workdir 相对形态经 _normalize_path 绝对化后作 base。
- F-3：_SUBPROC_IMPORTED_RE 重写（别名/star/多行括号/import subprocess as 四形态）。
- F-4：robocopy 撤出 _COPY_CMDS（半匹配假覆盖→声明边界，TC-R5-15 锁 PASS）。
- F-5：_DD_RE/_SED_PERL_RE 补 IGNORECASE。
- R4-1：-t 分支限 cp/install（rsync -t=preserve-times 不再误拦）。
- F-6：cwd 死键注释（防御纵深决策记录）。
- F-7：on_pre_tool_call 入口 args 非 dict 收敛 {}。
- OBS-1：deploy.py mirror_to_profiles（镜像到已存在 write-guard 的 profile；
  已实跑 architect/developer 两处，哈希一致）。

## 已登记不修（验证其登记完整性与理由即可，不算 finding）
F-8 双向、M-3 会话 cd 回退（R4-6）、tar/ln（N-8）、spawn-exec argv 族、
robocopy 三参、tool_call 泛化分发、exec/eval 套壳（N-7）。

## 复审纪律
只读；临时脚本写 reviews/audit-round5-{sec,qual}/；实测不采信自述；
复现 round4 全部原始场景（reviews/audit-round4/review-004.md 与
round4-review-20260922.md）确认封堵；攻击 round5 新代码面（_is_guard_dir_target
前缀误伤、门重写误拦回归、DOTALL 跨行过度匹配、deploy 镜像路径推导）；
最后 PASS / CHANGES REQUIRED。
