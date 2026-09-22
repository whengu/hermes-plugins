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

## 处置纪律
双路复审（deleg_aadc7cca / deleg_be807b34）在途以 4e254c8 为读取面，PM 不动代码。
回传后：若任一路报同形 → 并入 fix-013；均未报 → PM 按本差分补报（立项依据=本文件实测表）。
