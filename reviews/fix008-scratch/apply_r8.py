# -*- coding: utf-8 -*-
"""fix-008 handler.py 编辑器：F-7-1 引号感知续行归一 + F-7-2 =-粘连分支 + gateway 同源。
反斜杠密集行用整行前缀定位替换（CHANGELOG round7 教训：含转义序列的编辑走脚本）。"""
import io

P = "D:/myagent/workspace/write-guard/handler.py"
BS = chr(92)
NL = chr(10)
src = io.open(P, encoding="utf-8", newline="").read()
lines = src.split(NL)

HELPER = '''def _join_line_continuations(text):
    """F-7-1（round8）：引号感知续行粘连（取代 _judge_terminal 入口盲 replace——
    盲替换把成对反斜杠后的真换行也误当续行合并、且不认引号态，转义反斜杠形
    `echo a<2bs>LF cp evil <guard>` 两段被误并成一段=旁路）。引号外 反斜杠+LF
    （含反斜杠+CRLF）=shell 续行 → 删两（三）字符、行直接相接；单引号内字面
    不处理；双引号内不处理——按 2026-09-22 范围决策排除第 2 条登记接受边界，
    TC 锁现状。反斜杠逐对消耗，自然满足「成对不粘连、奇数末位单斜杠为字面」。"""
    NL, CR, SQ, DQ = chr(10), chr(13), chr(39), chr(34)
    out, i, n, quote = [], 0, len(text), None
    while i < n:
        ch = text[i]
        if quote == SQ:
            if ch == SQ:
                quote = None
            out.append(ch)
            i += 1
        elif quote == DQ:
            if ch == DQ:
                quote = None
            out.append(ch)
            i += 1
        elif ch == BS and i + 1 < n:
            nxt = text[i + 1]
            if nxt == NL:
                i += 2                          # 续行：反斜杠+LF 删两者
            elif nxt == CR and text[i + 2:i + 3] == NL:
                i += 3                          # 反斜杠+CRLF 同删
            else:
                out.append(ch)                  # 转义/成对反斜杠：两字符原样消耗
                out.append(nxt)
                i += 2
        else:
            if ch in (SQ, DQ):
                quote = ch
            out.append(ch)
            i += 1
    return "".join(out)


'''


def replace_line(prefix, newlines, label):
    idx = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert len(idx) == 1, "prefix not unique (%d): %s" % (len(idx), label)
    lines[idx[0]:idx[0] + 1] = newlines


# 1) helper 插到 def _judge_terminal 前
di = [i for i, l in enumerate(lines) if l.startswith("def _judge_terminal(")]
assert len(di) == 1
lines[di[0]:di[0]] = HELPER.rstrip(NL).split(NL) + [""]

# 2) 盲 replace 行 → 调用（前缀定位，反斜杠零依赖）
replace_line("    command = command.replace(",
             ["    command = _join_line_continuations(command)  # F-7-1（round8）引号感知粘连"],
             "blind-terminal")
replace_line("    text = text.replace(",
             ["    text = _join_line_continuations(text)   # F-7-1 同源：CRLF 续行一并封（红线 block 保持）"],
             "blind-gateway")

# 3) NL 注释块口径更新
ci = [i for i, l in enumerate(lines) if "反斜杠+换行=续行粘连回一行" in l]
assert len(ci) == 1
lines[ci[0]] = lines[ci[0]].replace(
    "反斜杠+换行=续行粘连回一行",
    "反斜杠+换行=续行，引号感知状态机删字符直接相接（round8 F-7-1 重写，禁盲 replace）")

# 4) F-7-2：norm 提取链补「引号选项词后 = 粘连」分支
ti = [i for i, l in enumerate(lines) if l.startswith("            norm_raw = raw.split")]
assert len(ti) == 1
lines[ti[0] + 1:ti[0] + 1] = [
    '        elif raw.startswith("=") and _COPY_T_QUOTED_RE.search(seg[:m.start()]):',
    '            # F-7-2（round8 灰区判=两行可修则做）：引号选项词后紧跟 = 粘连形',
    '            # cp "--target-directory"=<dir>——本 token 值即 = 后路径（选项词在',
    '            # 前一 token；判定仍由 -t 分支 _COPY_T_QUOTED_RE 门把关，保守收集）。',
    '            norm_raw = raw[1:]',
]

out = NL.join(lines)
assert "_join_line_continuations" in out and out != src
io.open(P, "w", encoding="utf-8", newline="").write(out)
print("patched OK; lines:", len(lines))
