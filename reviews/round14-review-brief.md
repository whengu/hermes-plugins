# Round14 双路复审任务书（安全路 sa-0 / 质量路 sa-1 共用）

工作目录 D:\myagent\workspace\write-guard。基线：git HEAD（代码 8611f3c 态，handler
sha256 前 16=0a93ac9caf8ee25e，主部署+双镜像一致）；test_handler ALL PASS（29+4+363）。
规格 reviews/fix-014-input.md；制品 reviews/fix-014.md；CHANGELOG round14 节；准绳
requirements/requirement-20260922-boundary.md。

## 本轮改动（审查面）
- 改动A：`_pair_unquote` 接粘连入口全族四处匹配输入（`_GLUED_T_RE` /
  `--target-directory=` / `of=` / `_OUTPUT_FLAG_EQ_RE` 长形）+ 提取位点剥对引号视图。
- 改动B：`_OUTPUT_QUOTED_RE` 并 cluster 尾 o 支（单 dash、输出命令门后）。
- NOTES：fix-013 回填 / 口径调和 / 注释实名 / 教训固化句。

## 硬要求
1. 每条 finding 当前 handler 实测复现 + **端活证**（bash/curl/pwsh 真执行证语义；
   写操作只在 workspace 沙箱构造，禁触碰受保护路径）。CHANGELOG round14 教训句同样
   约束复审：引号剥离类必扫全族粘连入口（-o / -t / --target-dir / of= / 冒号 / 
   cluster+空格值 六类逐分支翻转+活证），禁只测被点名支。
2. 特别审邻域（round13 挖洞机制的教训面）：`_pair_unquote` 的**全部调用位点**（grep 
   清点）语义是否一致（判定视图 vs norm 视图有无串用）；`of=` 支剥引号后 `dd "of=x"` 
   与 `dd " of=x"`（引号内前导空格）等非对称形行为；`--output=` 死选项 block 是否
   扩扰 wget 真语义面；cluster 尾 o 支对 `"O"` 大写单字母、URL 含引号 o 尾词等误命中面。
3. 红线：cp/mv/rename 源位读不拦、cp 目标写弹卡、rm -r 拦截、gateway restart 拦截、
   引号整包非保护=PASS 零误拦。
4. 边界外（劈 token、变量间接、eval、编码混淆）只登记；Z 组双绑必败 PASS=语义正确禁特判。
5. 质量路另核：CHANGELOG round14 节逐句对拍 git 史+实测（含第 7 项审批超时的如实登记句、
   附录死选项句、口径调和句）；fix-013.md 回填内容与 r13 git 史一致性；注释/行长。
6. 制品纪律：报告先落骨架边测边 [DONE]；报告写 reviews/audit-round14-sec/review-014-sec.md
   / audit-round14-qual/review-014-qual.md；终答 ≤200 字只给裁决+finding 计数。
7. 不修改被审代码，不 git commit。
