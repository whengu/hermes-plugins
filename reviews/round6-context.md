# round6 复审基线（2026-09-22 13:0x）

被审对象：workspace/write-guard（git 8fa3fe1）+ 部署目录一致性 + deploy.py 镜像通道。
测试基线 ALL PASS 29+4+219（+TC-R6 11 条）。前轮报告：reviews/audit-round4/、
reviews/audit-round5-{sec,qual}/。

## round6 修复项（逐项验收）
- D1：_is_guard_dir_target 泛化（home 树内任意 plugins/write-guard 段，
  _GUARD_DIR_SEG_RE 段边界）+ _is_protected_config 镜像插件代码分支 + 收集面。
  profile 镜像目录的 write_file/patch/cp 写全部收口，读放行。
- C3：_COPY_T_RE 短形簇（-rt/-at 等含 t 且非字母尾）+ 长形 --target-directory
  （空格/= 粘连/词尾）+ -t 分支认 raw 前缀；cp -T 不误扩。
- C4：复制族末位=home 内目录（无尾分隔符）收集进矩阵→approve（带斜杠名实一致）；
  mv/读负例放行。
- F-Q1：robocopy 登记句改写为"零兜底声明边界"（注释+CHANGELOG 名实一致）。
- F-Q2：mirror_to_profiles .tmp→os.replace 原子换入、OSError 受控、失败不报成功。
- F-Q4：_SUBPROC_CALL_RE 补 getstatusoutput。
- 微疵：F-2 恒死支删除；L553 陈旧注释合并；TC-E70 标题改准确。

## 已登记不修（验登记完整性即可，不算 finding）
F-8 双向、F-Q3 star-import 覆写、F-Q5 ~/xcopy 跨家、M-3 会话 cd（R4-6）、
tar/ln（N-8）、spawn-exec argv、robocopy 三参、tool_call 泛化、N-7 exec/eval、
F-Q6（R4-3 dict 形保守方向）。

## 攻击重点（round6 新代码面）
_Guard_DIR_SEG_RE 段边界（write-guard-old 不误伤）、镜像目录泛化对非 write-guard
插件的扩面（应为零）、C3 短形簇误拦面（-mt/-nt/-st 等真实选项？）、C4 收集面
对未知命令的溢出、矩阵外分支对新 token 形态的相互作用、deploy 原子换入残余
（.tmp 残留时重跑）。

## 纪律（两路共同）
只读被审文件；临时脚本只写各自 reviews/audit-round6-{sec,qual}/；实测不采信
自述；**结论先写、报告先落盘、终答只复述要点（防输出截断）**；最后 PASS /
CHANGES REQUIRED。
