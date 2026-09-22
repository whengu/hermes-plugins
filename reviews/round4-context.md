# round4 复审基线（2026-09-22 00:4x）

被审对象不变（workspace/write-guard + 部署 diff 验证），基线变化：
- handler.py round3 修复已入库（git 69aafcf）：C-1 workdir 真实坐标、H-1 目录目标、
  N-1（getstatusoutput + from-import 门）、N-3（三引号入口折叠）、N-4（递归传基准）、
  N-5（位置参/dict 形）、N-6（rsync/robocopy 并入复制族）。
- 声明边界收缩（判定为"不做"，见 CHANGELOG round3 节，理由需复audit）：spawn/exec
  argv 族、tar -C/unzip -d/patch/ln/find -delete、exec/eval 套壳、tool_call 泛化、
  M-3 会话级 cd 跟踪、execute_code workdir（该参数不存在，schema 实证）。
- 测试基线：ALL PASS 29+4+192（新增 TC-R3-01~16）。
- 新过程教训（自查）：曾误报"TC-A-55 回归"（实为无）；_r3c 非原子写致中间态。

round4 审查重点：
1. round3 六项修复是否真到位（用 round2 复审报告的原始复现场景重放，勿信注释）；
2. 修复自身引入面：workdir/cwd 双键、from-import 门（误拦面）、三引号折叠（把代码
   里正常的三引号 docstring 内容折叠后是否制造新误判）、rsync 并入后 cp 分支的读方向
   负例、目录形态判定（raw 以分隔符结尾）的边界；
3. 上轮 finding 的处置完整性核对（N-7/N-8 降边界是否被记录且理由成立）；
4. 自由攻击（重点：多引号混排、跨行、编码变体）。
纪律同 round2：只读、实测、行号+证据+修法、中文、最终 PASS/CHANGES REQUIRED。
临时脚本写 reviews/audit-round4/。
