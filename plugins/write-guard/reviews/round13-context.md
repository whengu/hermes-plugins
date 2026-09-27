# Round13 终审基线（context）

- **基线 git sha**: `10a2094`（round13 修复闭环）
- **handler sha256 前 16**: `cf61f3291970a021`（主部署+双镜像，实测一致）
- **test_handler**: ALL PASS（29 scan + 4 hook + 347 new cases）
- **规格**: reviews/fix-013-input.md（含「PM 活证补充」节：双目标标志绑定→Z1/Z3 锁 PASS 禁特判）
- **落地制品**: reviews/fix-013.md（§0 全落；§A/§B/§N/§V 施工截断未回填，Q13-C 修正——权威记载见 CHANGELOG round13 节+git diff 10a2094；回填义务并入 round14 NOTES）

## 改动摘要
- 改动A（F-12-1+F-12-2）：PS per-cmd 目标表 `_PS_TARGET_FLAGS = {copy-item: Destination, tee-object: FilePath|LiteralPath}` + 派生三表（尾锚/绑定/冒号粘连），旧全局 `_PS_NAMED_TARGET_RE`/`_GLUED_NAMED_RE` 删除；命名支三分句重构（判写=本 cmd 目标标志尾锚/冒号绑定且未绑另一值；判读=已绑另一值→PASS 且否决末位；无绑定→末位启发）。X1~4/T1~3 封堵、K1~K11 锁形保持。
- 改动B（F-12-3）：`_pair_unquote` 剥成对引号仅入 `_GLUED_O_RE` 匹配输入（curl/wget/sort 门后，token 化/norm 链不经过）——E1~4 封堵、K13~K19 无扰动。

## PM 门禁实测（12 项全达标）
- pm_verify_013：**30/30**（基线 11 靶心 FAIL 全转绿、19 锁形零回退）
- _verify_r13 41 / r12 53 / r11 43 / r10 46 / r9 46 / r8 30 / r7 30 / r5 28 / r3 25：**全 0 失败**
- pm_verify_012：23 形零回退；红线四形：gateway=block、cp 配置=approve、Copy-Item 源位读=PASS、rm -r 分层=PASS

## 教训固化（写入 CHANGELOG round13 节）
「修复引入回归第 3 次」（r10→r11、r11→r12、r12→r13 三次同构：收窄/放宽词表把某一维语义压成更粗的全局形）。**固化规则：收窄/放宽词表类修复，验收面必须含 per-cmd 语义活证（pwsh/curl 真写实链），不能只跑判定翻转表。**

## 在途
- sa-0 施工子代理（sa-0-59555a31）交卷时撞输出截断（第 7 次）——制品先落盘纪律生效，核心产物（代码+TC+制品+CHANGELOG）零丢失，无需重做。
