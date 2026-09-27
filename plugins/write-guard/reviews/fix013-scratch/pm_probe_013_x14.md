# PM round13 在途挖洞立项候选 X-14-1（-t 族引号整包旁路，round13 改动B 覆盖不对称）

**日期**：2026-09-23，round13 双路复审在途期间（基线 git 10a2094 / handler cf61f3291970a021）。
**性质**：漏拦（旁路），属用户边界**纳入范围**（整词引号包一个完整 token，非"引号劈 token"族）。

## 复现（当前 handler 实跑，probe2/P10 已捕获）

| 形 | 命令 | judge | 应有 |
|---|---|---|---|
| 裸粘连 -t | `cp -t<PDIR> _src.txt` | **approve** | ✓ 正确（r7 L-1 已修） |
| 双引号包 -t | `cp "-t<PDIR>" _src.txt` | **PASS** | ✗ 旁路 |
| 单引号包 -t | `cp '-t<PDIR>' _src.txt` | **PASS** | ✗ 旁路 |
| 裸等号 --target-dir | `cp --target-directory=<PDIR> f` | **approve** | ✓ 正确 |
| 引号值 --target-dir | `cp --target-directory="<PDIR>" f` | **approve** | ✓ 正确 |
| **双引号整包** | `cp "--target-directory=<PDIR>" f` | **PASS** | ✗ 旁路 |

其中 `<PDIR>` = `D:\myagent\.hermes\plugins\write-guard`（守卫源码目录，受保护）。

## 端活证（真执行，非翻转表）

```
$ mkdir -p _tdir4 && cp "--target-directory=D:/myagent/workspace/_tdir4" _src.txt && ls _tdir4
_src.txt            ← 真写入，目标目录收到文件
$ cp "-tD:/myagent/workspace/_tdir2" _src.txt && ls _tdir2
_src.txt            ← 真写入
```

bash 剥外层引号后 token 与裸形**逐字节同义**，真实语义完全等价 → 判定端不同判 = 真旁路，
不是"半匹配假覆盖"（该类已被排除）。

## 根因（一句话）

round13 改动B 把 `_pair_unquote` **只接到 `_GLUED_O_RE`（curl/wget/sort 输出选项）匹配输入**，
同族的 `_GLUED_T_RE`（`-t` / `--target-directory` 目标目录选项）**未接**——覆盖不对称。

**定性（PM 自纠，防名实不实现象）**：本条**不是** round13 引入的回归——引号包 `-t` 形在
round13 前后均 PASS（round13 改动B 只接 `_GLUED_O_RE` 匹配输入，未触 `-t` 支）。定性为
**既有覆盖不对称**（同族 -o 已修、-t/--target-dir 未修）。与 r10→r11、r11→r12、r12→r13
三次"修复引入回归"不同根，但同属"只修被点名的支，不修同族邻支"的模式。教训句：
**引号剥离类修复，验收面必须扫全族粘连入口（-o / -t / --target-dir / 冒号形），逐分支活证。**

## 建议修法（最小改动，待双路复审返回后一次性派单）

`_GLUED_T_RE` 与 `--target-directory=` 粘连支的匹配输入同样接 `_pair_unquote` 一处
（比照 round13 改动B 的 `_GLUED_O_RE` 接法；整支在复制族门后，token 化/norm 链不经过——
F-7-2 禁令不回潮）。预计 2 行内。锁形要求：裸形/引号值形三对保持 approve 不回退；
非保护目录引号整包 `cp "-tD:\...\workspace" f` 保持 PASS 零误拦。

## 处置状态

登记为 **X-14-1 立项候选**，已 steer 送 sa-0（安全路）独立复核 + pwsh/bash 活证背书。
按 dev-pipeline 纪律，**本 PM 不在复审在途时改动被审文件**，待两路返回后合并 finding 一次性派 round14。
