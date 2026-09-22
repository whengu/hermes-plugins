# round7 复审基线（2026-09-22 15:0x）

被审对象：workspace/write-guard（git 90de321）+ 部署一致性 + deploy 镜像。
测试基线 ALL PASS 29+4+233（+TC-R7 14 条）；_verify_r7 30/30、_verify_r5 28/0、
_verify_r3 25/0。前轮报告：reviews/audit-round6-{sec,qual}/。

## round7 修复项（逐项验收）
- **NL（HIGH）**：_judge_terminal 入口 `\`+换行粘连归一 + 分段集加 `\n`/`\r`。
  D 卷 9 攻击形（NL cp guard/镜像/config、CRLF、truncate、install、rsync、
  --tdir、-t、续行）全封堵；读/workspace 写/无关命令负例零回潮。
- **Q-6-1**：_GLUED_T_RE（`-t<dir>`/`-t=<dir>` 粘连，getopt 余部=目标）+
  _COPY_T_QUOTED_RE（`'-t'`/`"-t"`/`'--target-directory'` 引号选项形）。
  负例：`-tr` 目标歧义放行、非 home 引号 -t 放行。_COPY_T_RE 头注释名实改正。
- **Q-6-2**：_is_guard_dir_target 死支删除，字面量收敛 _GUARD_DIR_SEG_RE 单源。
- **Q-6-3**：长行规范多行；C4 注释补"任意末位 token 含文件=保守方向"。
- **Q-6-4**：.tmp=幂等暂存+排障证据不自动清理（docstring 声明）；TC-E71 不改
  （其语义仍是放行方向负例，名实无分叉）。

## 已登记不修（验登记完整性即可）
F-8 双向、F-Q3、F-Q5 ~/xcopy、M-3 会话 cd（R4-6）、tar/ln（N-8）、spawn-exec
argv、robocopy 三参零兜底、tool_call 泛化、N-7、F-Q6（R4-3 dict 形）。

## 攻击重点（round7 新代码面）
- NL：引号内换行是否真不切（多行字符串负例）、`\n` 分段对 cd 链跨行的影响、
  `\`+CR+LF 双形归一顺序（先 CRLF 后 LF 是否漏形）、正则字符串字面量里含换行的
  execute_code 假阳性。
- _GLUED_T_RE：`-t` 粘连对未知命令（-tpath 非 cp 族）是否被 cmd in (cp,install)
  门挡住；`-stage`/`-top` 等含 t 长词粘连是否误命中（[a-zA-Z]*t=? 贪婪）。
- _COPY_T_QUOTED_RE：before 含 `"--target"` 前缀误命中？引号内出现 '-t' 文本
  读命令（grep "'-t' " file）假阳性面。
- 分段集加 `\r` 对 Windows 原生多行脚本形态的影响。

## 纪律
只读被审文件；脚本写 reviews/audit-round7-{sec,qual}/；实测不采信自述；
**输出纪律（硬要求）**：全部分析与结论先写入 review-007-{sec,qual}.md，
终答只允许 ≤800 字符：裁决（PASS/CHANGES REQUIRED）+ 每条 finding 一行。
终答超长=任务失败。
