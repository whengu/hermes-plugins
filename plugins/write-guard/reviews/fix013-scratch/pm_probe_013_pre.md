# PM 主动挖洞差分（2026-09-23 01:0x，round12 基线 4e254c8，只读探针）

## 疑似 round13 finding（待双路回传后合并/PM 补报）

**X-13-1（候选 MED，纳入范围误拦+旁路双向）**：round12 TARGET 收窄（Q-11-1 修复）后，
末位否决子句 `and (not named or _PS_NAMED_TARGET_RE.search(before))` 只看"段内有无标志"、
不看"标志绑定的是谁"——「目标已绑 CFG + 后随其他命名标志」形漏拦：

| 形（PS 语义：Destination=写目标） | 实测 | 期望 |
|---|---|---|
| X1 `Copy-Item -Destination <CFG> -Path <ws>` | **PASS** | approve/block（CFG 是写目标） |
| X2 `Copy-Item -Destination <CFG> -LiteralPath <ws>` | **PASS** | 同上 |
| X3 `Copy-Item -Destination:<CFG> -Path <ws>`（冒号+后随标志） | **PASS** | 同上 |

对照锁形全保持（非本洞回归面）：
- C1 `-Destination <CFG> <位置参>` = approve ✓（r11 封堵形）
- C2 `-Container <CFG> -Destination <非保护>` = PASS ✓（r10 双标志锁，CFG 确为源）
- C3 `-Path <CFG> <非保护>` = PASS ✓（Q-11-1 归正形）
- X4 `Tee-Object -FilePath <CFG> -InputObject x` = approve ✓（InputObject 不在 ANY 表，无否决）
- X5 `-Destination <CFG> -Recurse` = approve ✓（同上）

根因链：Q-11-1 修复把 TARGET 收窄后，`-Destination <CFG>` 的 token 判写依赖
before 尾锚 TARGET 词；但 CFG token 后还有 `-Path` 时，**末位**变成 ws →
末位否决子句 named=True 且 before(ws)=`-Path` 尾锚 TARGET？否（Path 已移出 TARGET）
→ `_PS_NAMED_TARGET_RE.search(before of ws)` False → 末位支拒判 → CFG token 的
前置支 `search(before)` True 但 `not ANY(seg[m.end():])` False → 前置支也拒 → 整条 PASS。
即前置支的"后随标志→目标另有其主"假设只对 Container 类源参前置形成立，
对「真目标先绑、源参标志后随」反向排列不成立。

候选修法（≤4 行，规格 round13 定）：前置支条件改为
`not _PS_NAMED_ANY_RE.search(seg[m.end():]) or _PS_NAMED_TARGET_RE.search(seg[m.end():].lstrip() + " ")`
之类"后随标志仍为目标词则不否决"——精确形态留给 FIX，行为以本表+X/C 全列为验收。

## 邻域负例实测（均正确，不立项）
N1 `curl --http1.0 <CFG>`=PASS（数字尾不吃 ✓）；N2 `curl -Oso <CFG>`=block ✓；
N3 `wget -O-`=PASS ✓；N4 `curl "-o" <非保护>`=PASS ✓；N5 `sort /O<CFG>`=block ✓；
N6 `-Destination:"<CFG>"` 引号值=approve ✓。

## X-13-2（候选 MED，PS 活证实锤）Tee-Object -LiteralPath = 目标语义漏拦
实测（round12 基线）：
- T1 `Tee-Object -LiteralPath <CFG>` → PASS；T2 冒号形 → PASS；
  T3 `-InputObject x -LiteralPath <CFG>` → PASS；对照 T4 -FilePath CFG → approve ✓。
**pwsh 活证**：`Tee-Object -LiteralPath D:/…/\_live_t.txt` → 文件真实写出
（Tee-LiteralPath-wrote: True）。PS 语义：Tee-Object 的 -LiteralPath 是 -FilePath
的指定集成员（输出目标），与 Copy-Item 的 -LiteralPath（源参）**语义相反**。
TARGET 收窄为全局 {Destination,FilePath} 时把 per-cmd 语义压平所致。

## pwsh 活证补强 X-13-1
`Copy-Item -Destination <dst> -Path <src>` 组合合法运行且写入 Destination
（Dest+Path-combo-runs: True）——X1/X2/X3 是真可执行旁路，非理论形。

## 根因合并（X-13-1 与 X-13-2 同根）

### PM 补测（01:2x）+ 修法推演定稿
枚举后随标志：`-Destination <CFG>` 后随 -WhatIf/-Force/-Recurse（不在 ANY 表）→
approve 正常命中；后随 -Path/-Container（ANY 表源参）→ PASS 漏拦。**精确根因**：
前置支否决子句 `not _PS_NAMED_ANY_RE.search(seg[m.end():])` 把 ANY 五词任何一个
后随都当"目标另有其主"，但语义上只有**目标族标志**（Destination/FilePath/冒号形）
后随才接管目标；-Path/-Container 是源参，不改变已绑定的 Destination 目标。
候选修法（推演全支路通过）：否决子句的搜索正则从 ANY_RE 换为目标族专用正则
（`-(?:Destination|FilePath)\b|^-(?:Destination|FilePath):` 同款，含冒号形）。
支路验证：C2（-Container CFG -Destination 非保护=PASS）CFG 绑非目标词前置支本不触发
✓；C1 后随位置参无标志 ✓；r11 双 Destination 接管形否决保持 ✓；X1/X2/X3 封堵 ✓。

### X-13-2 修法（per-cmd 目标表）
_PS_NAMED_TARGET_RE 的全局词表改按 cmd 分表：copy-item→{Destination}、
tee-object→{FilePath, LiteralPath}（pwsh 活证 Tee -LiteralPath 真写目标）；
_GLUED_NAMED_RE 冒号形词集同步分 cmd。两处改动合计预估 ≤8 行（一个 dict + 取表一行 +
正则参数化），仍零新解析层。
锁形保全清单（round13 验收必测，全部现值不得回退）：
C1 approve / C2 PASS / C3 PASS / c1/c2/c5 PASS / X4/X5 approve / X8/X9 approve /
T4 approve / TC-R11 全部 / TC-R12 全部；新封堵期望：X1/X2/X3/T1/T2/T3 命中
（写配置=approve 弹卡、写守卫=block 按既有处置分流）。

## 处置纪律
双路复审（deleg_aadc7cca / deleg_be807b34）在途以 4e254c8 为读取面，PM 不动代码。
质量路已回 PASS；待安全路回传后：其 finding + 本文件 X-13-1/X-13-2 合并立 fix-013
一次性派单（立项依据=本文件实测表+pwsh 活证输出）。

## PM 活证补记（01:2x）：curl cluster `=` 形不立项（行为语义正确）
复审差分出现 `curl -sfo=<CFG>`=PASS。curl 8.1.2 file:// 活证：
- `curl -sfo _dst1.txt file:///…` exit=0 真写 _dst1.txt（空格形=真写，判定已封）；
- `curl -sfo=_dst2.txt file:///…` exit=0 但**实际落盘文件名是 `=_dst2.txt`**
  （字面带等号）——Windows curl 不吃 cluster `=` 分隔。
∴ 判定端不拦 `-sfo=<CFG>` 恰与 curl 真实语义一致（它并不写 `<CFG>`），无旁路无 FP。
sa-0 附录"等号形拒绝"的措辞系 PS 域（-Destination= 被 pwsh 拒），curl 域是"等号入
文件名"——语义不同但结论同向（该形不构成对目标路径的写）。**不立项，仅观察记录。**
