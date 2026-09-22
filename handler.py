"""write-guard: Hermes 工具调用前置守卫（pre_tool_call hook）。

四项独立守卫，按固定顺序 [D, C, A, B] 轮询，命中即返回（详见 ⑤ 调度器区）：
  D  Gateway 生命周期命令禁令   hermes gateway restart|run|start → block
  C  临时目录拦截              命令/代码/路径引用系统临时目录 → block
     （读取方向工具 _READ_TOOLS 无条件放行，不扫描其参数）
  A  配置写保护                HERMES_HOME 内配置文件写入 → block / approve
     write_file / patch 直接编辑 → block（必须走 safe-config-modify skill）
     terminal / execute_code    cp 类 → approve（弹审批）；其他写形态 → block
  B  记忆写保护                记忆写入工具 → approve（弹审批）

修订史与缺陷考古见 reviews/CHANGELOG-20260921.md（本文件注释只写设计理由，
不写「曾经错在哪」——独立工程质量审查 S-1）。
"""

import logging
import os
import re

logger = logging.getLogger(__name__)

# 通用模式组：路径字样 + 环境变量引用（IGNORECASE，Windows 路径大小写不敏感）
_BLOCK_PATTERNS = [
    # unix / MSYS 风格：/tmp、/tmp/xxx、/var/tmp、/usr/tmp
    # (?![\w-]) 防误伤连字符目录名（如 workspace/tmp-reports）
    r"/tmp(?![\w-])",
    # windows 反斜杠风格：\tmp、C:\tmp
    r"\\tmp(?![\w-])",
    # temp 作为路径组件：$LOCALAPPDATA/Temp、C:\Users\x\AppData\Local\Temp、…\Temp 结尾
    r"[\\/]temp(?:[\\/]|$)",
    # 环境变量引用：$TMPDIR ${TMPDIR}
    r"\$\{?tmpdir\}?(?![\w])",
    # $TMP ${TMP}
    r"\$\{?tmp\}?(?![\w])",
    # $TEMP ${TEMP}
    r"\$\{?temp\}?(?![\w])",
    # cmd 风格：%TEMP% %TMP%
    r"%temp%",
    r"%tmp%",
    # powershell 风格：$env:TEMP $env:TMP
    r"env:(?:temp|tmp)\b",
]

# 仅 shell 命令追加：裸 mktemp 默认写 /tmp
_SHELL_ONLY_PATTERNS = [
    r"\bmktemp\b",
]

# 仅代码追加：Python 标准库临时目录 API（默认写系统 Temp）
_CODE_ONLY_PATTERNS = [
    r"\btempfile\b",
    r"\bgettempdir\b",
    r"\bTemporaryDirectory\b",
    r"\bNamedTemporaryFile\b",
    # Python 读取临时目录环境变量：os.environ["TMP"] / os.environ.get('TEMP') / os.getenv("TMPDIR")
    r"(?:os\.environ(?:\.get)?\s*[\[(]|os\.getenv\s*\()\s*['\"](?:TMPDIR|TMP|TEMP)['\"]",
]

_COMPILED = {
    "shell": [
        re.compile(p, re.IGNORECASE) for p in _BLOCK_PATTERNS + _SHELL_ONLY_PATTERNS
    ],
    "code": [
        re.compile(p, re.IGNORECASE) for p in _BLOCK_PATTERNS + _CODE_ONLY_PATTERNS
    ],
}

# 工具名 → (检查的参数名, 模式组)
_TOOL_ARG_MAP = {
    "terminal": ("command", "shell"),
    "execute_code": ("code", "code"),
    "write_file": ("path", "shell"),
    "patch": ("path", "shell"),
}

# 读取方向工具集合（REQ-C1-01）：无条件放行、不扫描任何参数。
# 理由：读取类调用出现临时目录字样只表示「读哪里」，无写盘风险；搜索/读取
# 临时目录是合法操作，扫描其参数只会造成误拦。清单刻意收敛到最核心的 5 项，
# 其余工具（含 process_manage、web_extract、skill_view 等带副作用或语义不明
# 者）一律走参数检查，宁可保守也不放过写能力被低估的工具。
# 维护：Hermes 新增读取工具时需人工确认其纯读后加入本集合（收敛依据与
# 源码核实记录见 CHANGELOG）。
_READ_TOOLS = frozenset({
    # 文件读取与搜索（纯读，最高频）
    "read_file",
    "search_files",
    # 网络搜索（纯读）
    "web_search",
    # 记忆查询（纯读；hindsight_retain 写工具不在此清单，仍走 B 守卫审批）
    "hindsight_recall",
    "hindsight_reflect",
})

_DENIED_MESSAGE = (
    "write-guard 拦截：内容中出现系统临时目录引用（命中：{hit}）。"
    "用户规则：一切临时文件/下载只准写 D:\\myagent\\workspace\\"
    "（Hermes 配置目录 D:\\myagent\\.hermes 下的修改须走 safe-config-modify "
    "skill 流程），禁止写系统临时目录。请改用工作区路径后重试。"
)


# =====================================================================
# ① 常量区（A 项新增，DR-05/DR-06/DR-08/DR-12/DR-13/DR-21）
# =====================================================================

# A 项：HERMES_HOME 回退默认值（需求文档 1.5 节当前值示例；判定基准永远先取
# 运行时环境变量，DR-05——环境变量未设置或为空字符串时回退本默认值）
_DEFAULT_HERMES_HOME = r"D:\myagent\.hermes"

# 归一化统一分隔符常量（DR-21）：归一化将路径分隔符统一为正斜杠，因此所有
# 前缀拼接 / 前缀比对 / 文件名提取一律使用本常量。禁用 os.sep：Windows 下
# os.sep 为反斜杠，与全正斜杠的归一化目标拼出混合分隔符前缀会导致 A 项
# 前缀判定静默全失效（fail-open 方向）。
_SEP = "/"

# A 项最低强制工具覆盖集（FR-02 / DR-08）：其他工具一律不扫描、直接放行
# 不变量（S-4，测试断言锁定）：本集合必须 ⊆ _TOOL_ARG_MAP 键集——否则 A 守卫
# 新增工具在 C 面走兜底扫描、在 A 面零覆盖，两守卫覆盖面静默分叉。
_CONFIG_SCAN_TOOLS = ("write_file", "patch", "terminal", "execute_code")

# B 项写工具清单（FR-07 / DR-13，精确集合匹配，与参数无关）：
#   - hindsight_retain ：hindsight 插件写工具（源码路径 plugins/memory/hindsight/
#     __init__.py，RETAIN_SCHEMA 注册，写 hindsight 记忆库）
#   - memory           ：内置 memory 写工具注册名（源码路径 tools/memory_tool.py，
#     registry.register(name="memory")，写内置记忆库 MEMORY.md / USER.md）
#   - context_notes    ：内置 memory 写工具的 OAuth 线上别名（源码路径
#     agent/anthropic_adapter.py::_OAUTH_TOOL_NAME_ALIASES，{"memory": "context_notes"}，
#     需求文档点名形态，模型可见工具名之一）
# 查询工具（hindsight_recall / hindsight_reflect 及 memory 相关查询）不在清单内，
# 判定为「工具名 ∈ 写清单 → 命中；否则 → 放行」，查询自然放行（FR-08）。
_MEMORY_WRITE_TOOLS = frozenset({
    "hindsight_retain",
    "memory",
    "context_notes",
})

# A 项审批消息模板（FR-06 / 第 6 节）：汉字表述；{path} 为展示路径
# （字面命中=用户原文 DR-16；变体命中=原文（对应文件：<绝对路径>）DR-24）
_CONFIG_APPROVE_TEMPLATE = (
    "write-guard 配置写保护：工具「{tool_name}」将写入受保护的 Hermes 配置文件："
    "{path}。修改 Hermes 配置须经您批准，请确认后继续。"
)

# B 项审批消息模板（FR-09 / 第 6 节）
_MEMORY_APPROVE_TEMPLATE = (
    "write-guard 记忆写保护：工具「{tool_name}」将写入记忆库。"
    "未经您的批准不得写入记忆，请确认后继续。"
)

# A 项文件编辑工具 block 消息模板（用户决策 2026-09-21）：write_file/patch 直接
# 编辑受保护配置文件 → 不进审批、直接截断。必须走 skill 流程修改配置。
_SKILL_CONFIG_MODIFY = "safe-config-modify"   # R-5：skill 名单一来源（消息与测试共用）
_CONFIG_BLOCK_MESSAGE = (
    "write-guard 配置写保护：工具「{tool_name}」禁止直接编辑 Hermes 配置文件"
    "（{path}）。必须按照 skill 流程操作（" + _SKILL_CONFIG_MODIFY + "），不允许直接编辑配置文件。"
)


def _scan(kind: str, text: str):
    """返回命中的模式原文，未命中返回 None。"""
    for pat in _COMPILED[kind]:
        m = pat.search(text)
        if m:
            return m.group(0)
    return None


def _guard_tmpdir(tool_name: str, args: dict, task_id: str = "") -> dict | None:
    """守卫 C：临时目录拦截（v1.0 原始能力，行为向后兼容）。

    REQ-C1-01（2026-09-21）：读取方向工具（_READ_TOOLS 集合）**无条件放行**
    ——不扫描、不检查其任何参数。读取类工具的临时目录字样只表示读取/检索目标，
    无写入风险；搜索/读取临时目录是合法操作。
    写方向工具（_TOOL_ARG_MAP）与未知工具的兜底扫描行为保持不变。
    """
    if tool_name in _READ_TOOLS:
        logger.debug("write-guard: %s 为读取方向工具，临时目录字样放行", tool_name)
        return None
    mapped = _TOOL_ARG_MAP.get(tool_name)
    if mapped is not None:
        arg_name, kind = mapped
        texts = [args.get(arg_name)]
        if tool_name == "terminal":
            # C-cwd→round3 N-2 修正：平台 terminal 真实参数名是 workdir
            # （terminal_tool 签名实证：command/workdir/…，schema 无 cwd）。
            # 旧修复扫 args["cwd"] 打在不存在键上=零效果的假绿。两键并收。
            texts.append(args.get("workdir"))
            # cwd 是平台 schema 不存在的死键（F-6 round4）：保留扫描=防御纵深
            # 超集——幻觉参数 cwd=/tmp 会被拦（fail-closed 方向，代价可接受）。
            texts.append(args.get("cwd"))
        hit = None
        for t in texts:
            if isinstance(t, str) and t:
                hit = _scan(kind, t)
                if hit is not None:
                    break
    else:
        # 兜底：扫描该工具 args 中所有字符串值（如 chrome 截图 filePath）。
        # R-2 规则声明：兜底刻意选更宽的 code 组（含 tempfile/gettempdir 等
        # Python API 词）——未知工具的参数语义不可知，取宽集是"宁可多拦"；
        # 已知工具一律走 _TOOL_ARG_MAP 的精确 kind，不受此影响。
        kind = "code"
        hit = None
        for value in args.values():
            if isinstance(value, str):
                hit = _scan(kind, value)
                if hit is not None:
                    break

    if hit is None:
        logger.debug("write-guard: %s 未命中临时目录模式，放行", tool_name)
        return None

    message = _DENIED_MESSAGE.format(hit=hit)
    logger.warning(
        "write-guard: 拦截 %s（task=%s）— 命中模式 %r", tool_name, task_id, hit
    )
    return {"action": "block", "message": message}


# =====================================================================
# ② 模式编译区（A 项新增正则）
# =====================================================================

# 环境变量引用形态（归一化步骤 1 用，DR-23：完整词边界 + 统一大小写不敏感查找；
# 覆盖 %VAR% / $env:VAR / ${VAR} / $VAR 四种风格；词边界防 $HERMES_HOME2 误匹配前缀）
_ENV_VAR_NAME = r"[A-Za-z_][A-Za-z0-9_]*"
_ENV_REF_RE = re.compile(
    r"%(" + _ENV_VAR_NAME + r")%"
    r"|\$env:(" + _ENV_VAR_NAME + r")"
    r"|\$\{(" + _ENV_VAR_NAME + r")\}"
    r"|\$(" + _ENV_VAR_NAME + r")(?![A-Za-z0-9_])"
)

# 环境变量展开轮数（LOW-6 防御纵深：展开值内部可能再嵌套引用）
_ENV_EXPAND_ROUNDS = 2

# 热路径判定正则（②模式编译区，质量审查 R-8：判定函数内禁止内联 re.xxx，
# 全部集中预编译，保证单点维护 + 热路径性能）
_VERBATIM_PREFIX_RE = re.compile(r"^(?:\\\\\?\\|//\?/|//\./)")
_MULTI_SLASH_RE = re.compile(r"/+/")
_MSYS_FULL_RE = re.compile(r"^/(?:cygdrive/|mnt/)?([a-zA-Z])/(.*)$")
_MSYS_DRIVE_RE = re.compile(r"^/[a-zA-Z]/")
_ABS_PATH_RE = re.compile(r"^[A-Za-z]:/")
_SLASH_DRIVE_RE = re.compile(r"^/[A-Za-z]:/")
_WIN_ABS_RE = re.compile(r"^[A-Za-z]:[/\\]")
_DOT_SEGMENT_RE = re.compile(r"(?:^|[/\\])\.\.?(?:[/\\]|$)")
_SEG_HEAD_RE = re.compile(r"\s*([^\s;&|<>()]+)")
# S-4（round9 fix-009）：前导 wrapper 词与其后选项/环境赋值（仅剔除链中消费）
_COMMAND_WRAPPER_RE = re.compile(r"^(?:sudo|time|env|nohup|runas)$", re.IGNORECASE)
_ENV_ASSIGN_RE = re.compile(r"^[A-Za-z_]\w*=")
_DD_RE = re.compile(r"\bdd\b", re.IGNORECASE)          # F-5（round4）：DD 大写同拦
_SED_PERL_RE = re.compile(r"\b(?:sed|perl)\b", re.IGNORECASE)   # F-5：SED/PERL 大写同拦
# PowerShell 写 cmdlet（安全走查 F-A6）：受保护路径出现在其之后即写目标。
# 注意分支两组（F-9-1，round10）：仅 Set-Content/Add-Content/Out-File 走
# 「出现即写」支；Copy-Item/Tee-Object 是复制语义，摘出并入 _COPY_CMDS
# 末位/命名目标判定（源位=读不拦，与 cp 同语义不分叉；命名目标前置支系
# round11 fix-011 F-10-1 补建 _PS_NAMED_* 双正则，见 _terminal_position_is_write）。
_PS_WRITE_RE = re.compile(r"\b(?:Set-Content|Add-Content|Out-File)\b", re.IGNORECASE)
# cp/install -t <dir> 目标标志（F-A7）：-t 后紧跟受保护目录
_COPY_T_RE = re.compile(          # C3（round5 sa-0）：补长形 --target-directory
    r"(?:\s|^)-[a-zA-Z]*t(?![a-zA-Z])(?:\s|$)"   # 独立短形/词尾；短形簇 -rt/-at
    r"|(?:\s|^)--target-directory(?:\s|=|$)")   # 大写 -T 语义不同（GNU），不扩
# F-10-1（round11）：PS 复制族命名目标标志（比照 _COPY_T_RE 前置判据同款）。
# _PS_NAMED_ANY_RE=段内出现过该族标志（末位启发否决依据，`-Destination 非保护 CFG`
# 源位不再误弹）；五词表不动（规格 A4：named 前置条件保持全局在场检测）。
# F-11-3/Q-11-1（round12）：TARGET 词表收窄为目标词两词。
# F-12-1/F-12-2（round13）：全局 TARGET 词表压平了 per-cmd 语义（pwsh 活证：
# Tee-Object 的 -LiteralPath 是 -FilePath 指定集成员=输出目标，与 Copy-Item 的
# -LiteralPath=源参语义相反）——目标词表改按 cmd 分表，禁全局并集。
_PS_NAMED_ANY_RE = re.compile(
    r"-(?:Destination|FilePath|Path|Container|LiteralPath)\b", re.IGNORECASE)
_PS_TARGET_FLAGS = {"copy-item": r"Destination",
                    "tee-object": r"FilePath|LiteralPath"}
# 尾锚=本 token 紧随本 cmd 目标标志即其绑定值；bind 形=段内该标志已绑定值（含
# 冒号/=形，等号形 pwsh 活证拒绝→仅作"已绑另一值"否决信号，不当绑定命中）。
_PS_TAIL_ANCHOR_RES = {c: re.compile(r"-(?:%s)\s*$" % w, re.IGNORECASE)
                       for c, w in _PS_TARGET_FLAGS.items()}
_PS_TGT_BIND_RES = {c: re.compile(r"-(?:%s)(?:\s|[:=])" % w, re.IGNORECASE)
                    for c, w in _PS_TARGET_FLAGS.items()}
# F-11-1（round12）冒号粘连按 cmd 分表（round13 参数化，实名 _PS_GLUED_NAMED_RES，
# Q13-E 注释实名修正——旧全局 _GLUED_NAMED_RE 已删）：
# `-Destination:<值>`/`-LiteralPath:<值>`（含引号值）；等号形活证拒绝=附录不修。
_PS_GLUED_NAMED_RES = {c: re.compile(r"^-(?:%s):(['\"]?)(\S+?)\1$" % w, re.IGNORECASE)
                       for c, w in _PS_TARGET_FLAGS.items()}
# F-12-3（round13）：成对外层引号（匹配输入剥一处专用，禁入 token 化——F-7-2）
_PAIR_QUOTE_RE = re.compile(r"^(['\"])(.*)\1$")
# Q-6-1（round7）：GNU 合法粘连短形 -t<dir> / -t=<dir>（cluster 在前、t 收尾，
# 余部即目标值，与 getopt 语义一致）；另收引号选项形 cp"-t" 等
# （shell 剥引号后与裸 -t 同义；字符类用 x27/x22 十六进制形避开 raw 串引号）。
_GLUED_T_RE = re.compile(r"^-[a-zA-Z]*t=?(\S+)$")
# F-11-1（round12）：PS 冒号粘连 `-Destination:<值>`/`-FilePath:<值>`（含引号值；
# 等号形/全词粘连 pwsh 活证拒绝=附录不修）。提取值段进 norm，判定走命名支语义。
# F-12-1/2（round13）：全局两词表压平 per-cmd 语义（Tee 目标含 LiteralPath），
# 由 _PS_GLUED_NAMED_RES 按 cmd 分表接管，旧全局形删除。
# S-1（round9 fix-009）：-o<file>/-O<file> 粘连提取（=形已有 _OUTPUT_FLAG_EQ_RE；--output 长形双 dash 开头不匹配本形）
# F-9-3（round10）：字符类 ^- → ^[-/]，收 cmd 原生 sort /O<file> 粘连方言
_GLUED_O_RE = re.compile(r"^[-/][a-zA-Z]*[oO](?!=)(\S+)$")
_COPY_T_QUOTED_RE = re.compile(r"[\x27\x22](?:-t|--target-directory)[\x27\x22]")
_INPLACE_I_RE = re.compile(r"(?:\s|^)-p?i(?![\w-])")   # -i / -pi / -i.bak / -pi.bak
_INPLACE_LONG_RE = re.compile(r"--in-place(?![\w-])")    # --in-place / --in-place=.bak
_OPEN_WAX_RE = re.compile(r"[wax]")

# execute_code 写形态正则（DR-10 / 3.2.3）
_OPEN_WRITE_RE = re.compile(          # open(路径, 模式)；容忍 r/b/f 字符串前缀
    # （M-2：位置第二参后允许追加参数如 encoding=；第二参亦可 mode= 命名形态）
    r"\bopen\s*\(\s*(?:[rbfuRBFU]{0,2})(?P<q1>['\"])(?P<path>.*?)(?P=q1)"
    r"\s*,\s*(?:mode\s*=\s*)?(?:[rbfuRBFU]{0,2})(?P<q2>['\"])(?P<mode>[^'\"]*)(?P=q2)"
    r"\s*[,\)]", re.DOTALL)
_PATH_WRITE_RE = re.compile(          # Path(路径).write_text/write_bytes/touch
    r"\bPath\s*\(\s*(?:[rbfuRBFU]{0,2})(['\"])(.*?)\1\s*\)\s*\.\s*"
    r"(?:write_text|write_bytes|touch)\s*\(", re.DOTALL)
_PATH_OPEN_RE = re.compile(           # Path(路径).open(模式)
    r"\bPath\s*\(\s*(?:[rbfuRBFU]{0,2})(['\"])(.*?)\1\s*\)\s*\.\s*open\s*\(\s*"
    r"(?:[rbfuRBFU]{0,2})(['\"])([^'\"]*)\3\s*\)", re.DOTALL)
_SHUTIL_COPY_RE = re.compile(         # shutil.copy/copyfile/copy2(源, 目标)
    r"\bshutil\.(?:copy|copyfile|copy2)\s*\(\s*(?:[rbfuRBFU]{0,2})(['\"])(.*?)\1"
    r"\s*,\s*(?:[rbfuRBFU]{0,2})(['\"])(.*?)\3\s*\)", re.DOTALL)
_OS_OPEN_RE = re.compile(             # os.open(路径, 标志)
    r"\bos\.open\s*\(\s*(?:[rbfuRBFU]{0,2})(['\"])(.*?)\1\s*", re.DOTALL)
_TOOL_CALL_PATH_RE = re.compile(      # 代码内工具调用（N-5 三形态）：
    # write_file(path='x') / write_file('x',…) 位置参 / "path":'x' dict 形
    r"\b(?:hermes_tools\.)?(?:write_file|patch)\s*\(\s*(?:path\s*=\s*)?"
    r"(?:[rbfuRBFU]{0,2})(?P<q1>['\"])(?P<p1>.*?)(?P=q1)"
    r"|(?:'|\")path(?:'|\")\s*:\s*(?:[rbfuRBFU]{0,2})(?P<q2>['\"])(?P<p2>.*?)(?P=q2)",
    re.DOTALL)
_OS_WRITE_FLAGS = ("O_WRONLY", "O_RDWR", "O_CREAT", "O_APPEND", "O_TRUNC")
# 内嵌 shell 面（安全走查 F-A2）：execute_code 里 os.system / os.popen /
# subprocess.* 携带的 shell 命令字符串，复用 terminal 写矩阵判定。
# 命令行单参形态（cmd=整条 shell 命令行，可直接进 terminal 判定链）：
_OS_SYSTEM_RE = re.compile(
    r"\bos\.(?:system|popen|getstatusoutput)\s*\(\s*"
    r"(?:[rbfuRBFU]{0,2})(?P<q>['\"])(?P<cmd>.*?)(?P=q)", re.DOTALL)
# os.spawn*/os.exec* argv 族（N-1 评估后不做）：第一参是程序路径、写目标散在
# argv 后部，单参捕获只会半匹配（把程序名当命令行）形成假覆盖；正确判定需
# argv 语义解析，违背"不加复杂度"。降为声明边界（CHANGELOG）。
_SUBPROC_CALL_RE = re.compile(       # round3 N-1：subprocess. 限定形 + 裸词形两段
    r"\b(?:subprocess\.){1}(?:run|call|check_call|check_output"
    r"|Popen|getoutput|getstatusoutput)\s*\(")
# `from subprocess import run` 后的裸 run(...)：仅当代码含该 from-import 时才扫（防误拦）
# round4 F-3：门覆盖 from-import 的别名（run as r）/ 多行括号 / star（import *）
# 三形态，另收 `import subprocess as sp` 模块别名（组3→限定形按别名重建）。
_SUBPROC_IMPORTED_RE = re.compile(
    r"\bfrom\s+subprocess\s+import\s+(?:\(([^)]*)\)|([^\n#]*))"   # 括号形跨行
    r"|\bimport\s+subprocess\s+as\s+(\w+)", re.DOTALL)
_SUBPROC_FUNCS = ("run", "call", "check_call", "check_output", "Popen",
                  "getoutput", "getstatusoutput")
# M-1：terminal 段的内嵌 shell 载体——命令词为 shell 解释器且带 -c/-lc/-Command
# /-command-with-args，其引号内字符串是完整 shell 命令，递归复用 terminal 判定链。
_EMBED_SHELL_RE = re.compile(
    r"^\s*(?:pwsh|powershell(?:\.exe)?|cmd(?:\.exe)?|bash|sh|zsh|ksh|dash)"
    r"(?:\s+/[a-zA-Z]+)*"                       # cmd /c /k 等前导开关
    r"(?:\s+-NoProfile|\s+-NonInteractive|\s+[/-][a-zA-Z]+)*"
    r"\s+(?:-[lc]?c|-Command|-commandwithargs|/c|/k)\b"
    r"\s*(?P<q>['\"])(?P<body>.*?)(?P=q)\s*$", re.IGNORECASE | re.DOTALL)
# S-5（round9 fix-009）：载体裸形（引号体不成立时的 cmd /c copy… / pwsh -Command …）
_BARE_CARRIER_RE = re.compile(
    r"^\s*(?:pwsh|powershell(?:\.exe)?|cmd(?:\.exe)?|bash|sh|zsh|ksh|dash)"
    r"(?:\s+[/-][A-Za-z]\w*)*\s+(?:-[lc]?c|-Command|-commandwithargs|/c|/k)\b"
    r"(?P<rest>.*)$", re.IGNORECASE | re.DOTALL)
# 字符串字面量（subprocess 参数内容提取；list 形态逐项捕获后拼为命令文本）
_STR_LIT_RE = re.compile(r"(?:[rbfuRBFU]{0,2})(['\"])(.*?)\1", re.DOTALL)
# 互递归深度上限（terminal 内嵌 python ↔ execute_code 内嵌 shell）
_NEST_DEPTH_LIMIT = 3


# =====================================================================
# ③ 判定基础区（A 项新增，纯内存计算，NFR-05）
# =====================================================================

def _env_lookup(name: str):
    """环境变量大小写不敏感查找（DR-23）：Windows 平台 os.environ 原生大小写不敏感；
    POSIX 平台实现「键小写化比对」辅助查找，保证 $HERMES_home 等变体同样展开。
    未定义返回 None。"""
    val = os.environ.get(name)
    if val is not None:
        return val
    lower = name.lower()
    for key, value in os.environ.items():
        if key.lower() == lower:
            return value
    return None


def _expand_env(text: str) -> str:
    """环境变量展开（DR-23）：%VAR% / $VAR / ${VAR} / $env:VAR 统一走
    「完整词边界 + 大小写不敏感查找」内核；未定义变量保留原样。
    不依赖 os.path.expandvars（其对 %VAR% 与 $VAR 的大小写语义不一致）。
    LOW-6（防御纵深）：有限次递归——连续 2 轮替换，使变量值内部嵌套的引用
    （如 HERMES_HOME 值本身含 %USERPROFILE% 形态）同样展开，避免保护基准
    漂移；每轮为单次扫描、自引用形态在第二轮后保持原样，必然终止。"""
    def repl(m):
        for i in range(1, 5):
            name = m.group(i)
            if name:
                val = _env_lookup(name)
                return val if val is not None else m.group(0)
        return m.group(0)
    s = _ENV_REF_RE.sub(repl, text)
    for _ in range(_ENV_EXPAND_ROUNDS - 1):   # LOW-6：多轮展开值内嵌套引用
        s = _ENV_REF_RE.sub(repl, s)
    return s


# 路径文本解义（DR-22）：仅把成对双反斜杠（terminal 引号内的转义写法）解义为
# 单反斜杠；单反斜杠 + 任意字符一律按字面路径保留。
# 依据：归一化的输入是「用户写的路径文本」，不是「待求值的 Python 字符串字面量」
# ——安全判定不得依赖字符串转义语义（历史缺陷记录见 CHANGELOG）。
_DOUBLE_BACKSLASH = "\\\\"


def _unescape_string_literal(text: str) -> str:
    """仅将成对双反斜杠序列解义为单个反斜杠（terminal 命令引号内转义写法）；
    其余全部保留原样，路径判定按字面处理（DR-22）。"""
    return text.replace(_DOUBLE_BACKSLASH, "\\")


def _strip_outer_quotes(text: str) -> str:
    """整体被单/双引号包裹时去除两端引号（归一化步骤 2）。"""
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ("'", '"'):
        return text[1:-1]
    return text


def _normalize_path(text, base=None):
    """路径归一化（DR-07 / DR-22 / DR-27），任一步无法处理返回 None（Q-03 放行）。
    步骤（顺序即正确性的一部分，不可重排）：
      1 环境变量展开 → 2 去外层引号 → 3 verbatim 前缀剥离（\\?\\ 等）
      → 4 双反斜杠解义 → 5 分隔符统一（反斜杠→正斜杠）→ 6 连续分隔符压缩
      → 7 ~ 展开 → 8 MSYS/cygwin 盘符转换 → 9 相对段归一（. / ..）
      → 10 绝对化（base 缺省 os.getcwd()）→ 11 大小写归一
    相对路径基准（DR-27）：已对照 Hermes 源码 tools/file_tools_paths.py
    （_resolve_path_for_task / _resolve_base_dir）核实——write_file / patch 以
    task workspace root 为基准、无 workspace root 时回退进程 cwd；terminal /
    execute_code 以进程 cwd 为基准。本函数统一取进程 cwd：落差为显式声明的
    接受边界（论证见 _judge_path_param）。
    """
    if not isinstance(text, str) or not text.strip():
        return None
    s = _expand_env(text)
    s = s.strip()
    s = _strip_outer_quotes(s)
    if not s:
        return None
    # verbatim 前缀（\\?\\、\\.\\、//?/）不参与解义与压缩：必须先剥离，
    # 否则步骤 4 把 \\\\ 解义、步骤 6 把 //?/ 压成 /?/，前缀正则失配（DR-22 顺序约束）。
    s = _VERBATIM_PREFIX_RE.sub("", s)
    s = _unescape_string_literal(s)
    s = s.replace("\\", "/")
    s = _MULTI_SLASH_RE.sub("/", s)
    # ~ / ~/ 展开，与 Hermes 写端 get_subprocess_home()（file_tools_paths.
    # _expand_tilde）语义对齐——两侧基准不一致会造成同一路径的判定落差。
    if s == "~" or s.startswith("~/"):
        home_expand = os.path.expanduser("~").replace("\\", "/")
        if home_expand and home_expand != "~":
            s = home_expand.rstrip("/") + s[1:] if s != "~" else home_expand
    # MSYS/cygwin 形态转盘符：/d/x、/cygdrive/d/x、/mnt/d/x → d:/x。
    # 双条件是必要的：/cygdrive/ 与 /mnt/ 之后盘符在第 2/3 段（由 _MSYS_FULL_RE
    # 捕获），而单段形态 /d/ 必须确认「斜杠+单字母+斜杠」才转——否则 /tmp、/usr
    # 等 POSIX 根路径会被误判成盘符。
    msys = _MSYS_FULL_RE.match(s)
    if msys and (s.startswith("/cygdrive/") or s.startswith("/mnt/") or _MSYS_DRIVE_RE.match(s)):
        s = msys.group(1).lower() + ":/" + msys.group(2)
    if base is None:
        base = os.getcwd()
    if isinstance(base, str):
        base = base.replace("\\", "/")
    # 绝对路径判定须同时识别盘符形态（D:/... 不以 / 开头，DR-21 归一化后盘符
    # 绝对路径以 d: 开头）与根路径形态；其余按相对路径基于 base 拼接
    if not s.startswith("/") and not _ABS_PATH_RE.match(s):
        s = base.rstrip("/") + "/" + s
    parts = []
    for seg in s.split("/"):
        if seg in ("", "."):
            continue
        if seg == "..":
            if parts:
                parts.pop()
            continue
        parts.append(seg)
    result = "/" + "/".join(parts)
    # Windows 盘符形态 /d:/... → d:/...（去掉前导正斜杠）
    if _SLASH_DRIVE_RE.match(result):
        result = result[1:]
    return result.lower()


def _hermes_home() -> str:
    """HERMES_HOME 运行时实时读取（DR-05）：未设置或空字符串回退默认值；不缓存。"""
    raw = os.environ.get("HERMES_HOME") or _DEFAULT_HERMES_HOME
    norm = _normalize_path(raw)
    return norm if norm is not None else _normalize_path(_DEFAULT_HERMES_HOME)


# 受保护配置文件判定口径（用户决策 2026-09-21「范围要扩大」）：
# HERMES_HOME 内 + （扩展名 yaml/yml/json，或文件名含 config，或 .env 系列）
# → 受保护。skills/*.md、logs/、cache/ 等非配置文件不保护（保护范围与可用性
# 取前者）；**例外**：plugins/ 下 .py/.yaml/.yml 受保护（F-A3 反缴械，见下方
# _PLUGIN_CODE_EXTS——L-3 修正：原注释仍写"plugins/*.py 不保护"与代码矛盾）。
_CONFIG_EXTS = (".yaml", ".yml", ".json")
_CONFIG_NAMES = (".env",)
# 反缴械（安全走查 F-A3）：plugins/ 下代码与清单同样受保护——守卫自身源码若可
# 被 write_file 覆盖，全部保护形同虚设。改插件走 workspace 开发 + deploy.py
# 部署（部署命令文本不含受保护路径字面量，通道不受影响）。
_PLUGIN_CODE_EXTS = (".py", ".yaml", ".yml")


def _is_protected_config(norm_target: str) -> bool:
    """受保护判定（DR-06 / DR-21）：前缀匹配（HERMES_HOME 内）
    + 目标为配置文件（扩展名 yaml/yml/json 或文件名含 config 或 .env 系列）。
    前缀拼接 / 前缀比对 / 文件名提取统一使用正斜杠常量 _SEP，禁用 os.sep。"""
    home = _hermes_home()
    if norm_target == home:                      # 指向目录本身：非内容写入
        return False
    if not norm_target.startswith(home + _SEP):
        return False
    if norm_target.startswith((home + _SEP + "plugins") + _SEP) \
            and norm_target.rsplit(_SEP, 1)[-1].endswith(_PLUGIN_CODE_EXTS):
        return True                              # 插件代码/清单（F-A3 反缴械）
    # D1（round5 sa-0）：write-guard 镜像副本（<root>/profiles/<p>/plugins/
    # write-guard/*.{py,yaml,yml}）与主部署同等反缴械权重（profile 会话实际
    # 加载者），同受保护；其它插件文件不扩面。
    if (norm_target.startswith(home + _SEP)
            and _GUARD_DIR_SEG_RE.search(norm_target)
            and norm_target.rsplit(_SEP, 1)[-1].endswith(_PLUGIN_CODE_EXTS)):
        return True
    filename = norm_target.rsplit(_SEP, 1)[-1]
    lower = filename.lower()
    if lower.endswith(_CONFIG_EXTS):
        return True
    if "config" in lower:
        return True
    if lower.startswith(_CONFIG_NAMES):          # .env / .env.local 等
        return True
    return False


def _is_variant_hit(raw: str) -> bool:
    """等价类变体判定（DR-24）：环境变量引用 / 相对路径 / 转义字面量 / . .. 段
    → 消息双段展示；大小写与分隔符变体属字面形态，只展示原文（DR-16）。"""
    s = raw.strip()
    if not s:
        return False
    s = _strip_outer_quotes(s)
    if "\\\\" in s:                       # 转义字面量（两个连续反斜杠字符）
        return True
    if _ENV_REF_RE.search(s):             # 环境变量引用
        return True
    if not _WIN_ABS_RE.match(s) and not s.startswith(("/", "\\\\")):
        return True                       # 相对路径
    if _DOT_SEGMENT_RE.search(s):
        return True                       # . / .. 段
    return False


def _shown_path(raw_path: str, norm_target: str) -> str:
    """消息路径展示（变体命中时双段展示：原始写法 + 解析后绝对路径）。
    _approve_result / _config_block_result 共用（质量审查 S-2 去重）。"""
    if _is_variant_hit(raw_path):
        return f"{raw_path}（对应文件：{norm_target}）"
    return raw_path


def _approve_result(tool_name: str, raw_path: str, norm_target: str) -> dict:
    """A 项 approve 返回结构（DR-12 / DR-16 / DR-24）。"""
    return {
        "action": "approve",
        "message": _CONFIG_APPROVE_TEMPLATE.format(tool_name=tool_name, path=_shown_path(raw_path, norm_target)),
        "rule_key": f"write_guard:config:{norm_target}",
    }


def _config_block_result(tool_name: str, raw_path: str, norm_target: str) -> dict:
    """A 项 block 返回结构（用户决策 2026-09-21）：直接截断不进审批门，
    消息含目标文件路径 + skill 流程指引。"""
    return {
        "action": "block",
        "message": _CONFIG_BLOCK_MESSAGE.format(tool_name=tool_name, path=_shown_path(raw_path, norm_target)),
    }


def _judge_path_param(path, tool_name):
    """write_file/patch 路径参数判定（DR-26）：path 非字符串 / 空串 / 仅空白
    → 直接返回 None（放行），不进入归一化。

    LOW-3（接受边界声明）：Hermes 实际以 task workspace root 为相对路径基准、
    进程 cwd 兜底（已对照源码 tools/file_tools_paths.py 核实，见 _normalize_path
    注释）；本守卫以进程 cwd（os.getcwd()）为判定基准，与 Hermes 兜底基准一致。
    task 会话 cwd 与进程 cwd 不一致、且以相对路径写受保护目录时存在理论漏拦——
    该落差为显式声明的接受边界：task cwd 默认即进程 cwd、相对路径写受保护目录
    场景罕见，按 Q-03 低误拦优先原则放行；不在插件内复制 Hermes 内部路径解析
    逻辑（避免与 Hermes 实现漂移及潜在 IO，保持 NFR-05 纯内存）。

    用户决策（2026-09-21）：文件编辑工具直接编辑受保护配置文件 → block（直接
    截断，不进审批门），提示必须按 skill 流程操作。terminal/execute_code 的
    配置写保护仍走 approve（弹卡）。"""
    if not isinstance(path, str) or not path.strip():
        return None
    norm = _normalize_path(path)
    if norm is not None and _is_protected_config(norm):
        return _config_block_result(tool_name, path, norm)
    return None


# terminal 段内路径候选 token（引号整体或空白/符号分隔单词）
_PATH_TOKEN_RE = re.compile(r'"[^"]*"|\'[^\']*\'|[^\s;&|<>()]+')
# cd 目标捕获不跨越管道符（[^|]）：管道左侧的 cd 运行在子进程、不跨管道传播
# （设计 3.2.2），贪婪匹配会把管道后的写形态错误归因到 cd 目标。与
# _judge_terminal 的管道先行分段构成双保险（引号内管道等残余形态亦不外溢）。
_CD_PREFIX_RE = re.compile(r"^(?:cd|pushd)\s+(?:/d\s+)?([^|]+)$", re.IGNORECASE)
# rsync 与 cp 同为复制语义（末位参数=目标，复用现有分支零新逻辑，N-6）。
# tar -C/unzip -d/patch/ln/find -delete 需目标位语义解析或属
# 链接/改名族，按"不加复杂度"降为声明边界（CHANGELOG round3 记录）。
# 不含 robocopy（round4 F-4/R4-5）：robocopy 参数序是 src <dir> <file>——目标在
# 第 2 参、末位是文件名，cp 式"末位=目标"判定套不上，并入只会形成半匹配假覆盖
# （实测三参定向覆写漏拦）。正确处理需 robocopy 专属位参解析，违背"不加复杂度"
# → 降为声明边界（CHANGELOG）。注意：robocopy 写配置当前零兜底（不在复制族、
# 末位是文件名非目录，其余矩阵分支均不命中，round5 sa-1 F-Q1 实测），与其说
# "有兜底"不如如实登记为零覆盖边界。
_COPY_CMDS = ("cp", "copy", "install", "rsync",
              "copy-item", "tee-object")   # F-9-1（round10）：PS 复制族 cmdlet 并入同款判定
_MOVE_CMDS = ("mv", "ren")

# 输出参数形态（FR-02③「等」字范围）：已知带输出文件参数的下载/输出命令
# （curl -o/-O、wget -O、sort -o 等）其输出参数语义明确为写目标 → 判写；
# 未知命令带 -o/-O 无法确定语义 → 放行（Q-03 低误拦优先，不为未知工具猜意图）。
_OUTPUT_FLAG_CMDS_RE = re.compile(r"\b(?:curl|wget|sort)\b", re.IGNORECASE)
_OUTPUT_FLAG_RE = re.compile(
    # F-10-2（round11）：短形组加 token 独立约束（(?:^|(?<=\s)) 前随空白/段首，
    # [-/]o 大小写双收由 IGNORECASE 承担）——路径/URL token 以 /o、/O、-o 收尾
    # 不再误命中（r10 放宽回归）；长形与 = 粘连链语义不变。
    # F-11-4（round12）：并 dash 专属 cluster 尾 o 支 `-{1,2}[a-zA-Z]*o`（getopt
    # `-so <file>` 与 `-o <file>` 同义，S-1 家族第三写法）；斜杠方言不参与——cmd
    # 无 cluster 语义，F-10-2 的 `ws/o` 归正不回潮；`[a-zA-Z]*` 不吃数字。
    r"(?:--output-document|--output|(?:^|(?<=\s))[-/]o|(?:^|(?<=\s))-{1,2}[a-zA-Z]*o)"
    r"\s*(?:=\s*)?$", re.IGNORECASE)
# F-11-2（round12）：引号包输出选项词 `curl "-o" <file>`（shell 剥引号后与裸 -o
# 同义，curl 活证真写；比照 _COPY_T_QUOTED_RE 先例，整词成对、内容不可选、不做
# 通用引号剥离——F-7-2 禁令不回潮）。
# Q13-A（round14）：并引号包 cluster 尾 o 支 `["'][-][a-zA-Z]*[oO]["']`——引号内
# = cluster 字母串且尾字母 o/O（`curl "-so" <CFG>` 与裸 -so 同义，活证真写）；
# 字符类比照 _OUTPUT_FLAG_RE dash cluster 支同款，单 dash 专属（双 dash 红线不扩），
# 值走既有后随 token 判定；整支在 _OUTPUT_FLAG_CMDS_RE 门后，门外 grep "-so" 零扰动。
_OUTPUT_QUOTED_RE = re.compile(
    r"[\x27\x22](?:-[oO]|--output(?:-document)?|-[a-zA-Z]*[oO])[\x27\x22]\s*$")
_OUTPUT_FLAG_EQ_RE = re.compile(
    r"(?:--output-document|--output|-o|-O)=(.*)$", re.IGNORECASE)


def _command_word(seg: str):
    """命令段首个实词（命令名）。S-4（round9 fix-009）：循环剔除前导 wrapper 词
    （sudo|time|env|nohup|runas）、环境赋值词（LANG=C）、选项词（/c、-u——首个实词
    之前的连续位），取下一实词；全被剔除→None（按不可判定放行）。零新解析层。"""
    toks = [t.strip("'\"") for t in _SEG_HEAD_RE.findall(seg)]
    while toks and (_COMMAND_WRAPPER_RE.match(toks[0]) or _ENV_ASSIGN_RE.match(toks[0])
                    or toks[0][:1] in ("/", "-")):
        toks.pop(0)
    return toks[0].lower() if toks else None


def _pair_unquote(s: str) -> str:
    """F-12-3（round13）建，F-13-S1（round14）接线**粘连入口全族**：剥**成对**
    外层引号一处——仅供匹配视图（_GLUED_O_RE/_GLUED_T_RE/of=/--target-directory=/
    _OUTPUT_FLAG_EQ_RE 各支匹配输入）；token 化与 norm 链不经过此处（F-7-2 通用
    剥离禁令不回潮）。"""
    qm = _PAIR_QUOTE_RE.match(s)
    return qm.group(2) if qm else s


def _strip_wrapper_prefix(seg: str) -> str:
    """F-9-2（round10）：复用 _command_word 剔除链（wrapper 词/环境赋值/前导选项），
    但返回剔除后的**剩余文本**（无剔除则原样）——供载体正则先于原文尝试匹配，
    打通 wrapper×载体组合通道（sudo bash -c "…" / LANG=C pwsh -Command …）。"""
    toks = list(_SEG_HEAD_RE.finditer(seg))
    i = 0
    while i < len(toks):
        w = toks[i].group(1).strip("'\"")
        if (_COMMAND_WRAPPER_RE.match(w) or _ENV_ASSIGN_RE.match(w)
                or w[:1] in ("/", "-")):
            i += 1
        else:
            break
    return seg[toks[i - 1].end():] if i else seg


_GUARD_DIR_SEG_RE = re.compile(
    r"(?:^|/)" + "plugins" + "/" + "write-guard" + r"(/|$)")


def _is_guard_dir_target(norm) -> bool:
    """F-1（round4，HIGH）：norm 指向守卫插件自身目录（…/plugins/write-guard）。
    Windows 语义下 cp 目标是目录时可不带尾分隔符（`cp evil D:\\...\\write-guard`
    与带斜杠同义，实测轮3 仅拦带斜杠形态=反缴械链仍开）。凡复制目标指向守卫
    目录（含无分隔符形态）一律按写目标处置——覆写 handler.py/plugin.yaml 即
    缴械全部保护，此处宁拦勿漏（该目录作为复制末位目标无合法写场景）。"""
    if norm is None:
        return False
    # D1（round5 sa-0）：OBS-1 镜像后 profile 会话加载
    # <root>/profiles/<p>/plugins/write-guard/ 副本——守卫目录识别不限主 home，
    # 任何 root 下的 plugins/write-guard 路径段均为反缴械目标（段边界匹配，
    # write-guard-old 等同前缀目录不误伤）。
    # Q-6-2（round7）：round5 泛化后主守卫目录独立分支恒不可达（候选集实证
    # b2 且非 b1=空集：主目录本身在 home 树内被首条件覆盖）——删支，
    # write-guard/plugins 字面量收敛 _GUARD_DIR_SEG_RE 单一来源（Q-6-4 尾项）。
    return norm.startswith(_hermes_home() + _SEP) and _GUARD_DIR_SEG_RE.search(norm) is not None


def _terminal_position_is_write(seg: str, m, raw: str, norm: str, cwd: str) -> bool:
    """terminal 写语义判定矩阵（DR-09 / 3.2.2）。返回 True=写（拦）；False=读/无法判定（放行）。"""
    start = m.start()
    before = seg[:start].rstrip()
    # 输出重定向 > / >>（含 1> 2> &>）→ 写
    if before.endswith(">"):
        return True
    # 输入重定向 < → 读
    if before.endswith("<"):
        return False
    # dd of=路径 → 写
    # F-13-S1-A3（round14）：匹配输入接 _pair_unquote（仅判定视图，引号整包
    # `dd "of=<CFG>"` 与裸形同义；norm 链不经过——F-7-2 禁令）
    if _pair_unquote(raw).lower().startswith("of=") and _DD_RE.search(before):
        return True
    # tee 目标 → 写（全部位参皆目标，POSIX tee 语义；F-9-4 round10：判据由
    # "前一词==tee"改为"段命令词==tee"，非末位多目标形不再漏拦）
    if _command_word(seg) == "tee":
        return True
    # 输出参数（curl/wget/sort 的 -o/-O/--output，含 = 粘连形态）→ 写目标；
    # 未知命令的 -o/-O → 放行（语义不可判定，Q-03）。
    if _OUTPUT_FLAG_CMDS_RE.search(before):
        # F-11-2（round12）：or 支=引号包选项词（curl "-o" <CFG>，shell 剥引号
        # 后与裸 -o 同义；比照 _COPY_T_QUOTED_RE 先例，不做通用引号剥离）
        _raw_ou = _pair_unquote(raw)   # F-13-S1-A4：--output= 长形引号整包（curl 端
        # 死选项 `=` 并入文件名活证，block=无害多防，比照 r13 -o= 附录句）
        if (_OUTPUT_FLAG_RE.search(before)
                or _OUTPUT_FLAG_EQ_RE.match(_raw_ou)
                # F-12-3（round13）：匹配输入剥成对引号一处（`curl "-o<CFG>"` 与
                # 裸形同义；整支有 _OUTPUT_FLAG_CMDS_RE 门=仅 curl/wget/sort，零
                # 扰动复制族；token 化/norm 链不经过此——F-7-2 禁令）
                or _GLUED_O_RE.match(_raw_ou)   # S-1：-o<file> 粘连形
                or _OUTPUT_QUOTED_RE.search(before)):  # F-11-2：引号选项词形（r14 并 cluster 尾 o）
            return True
    # 原位编辑 sed -i / perl -pi → 写
    if _SED_PERL_RE.search(before) and (
            _INPLACE_I_RE.search(before) or _INPLACE_LONG_RE.search(before)):
        return True
    # 复制类：受保护路径为命令中最后一个路径参数 → 目标写；为源 → 读
    cmd = _command_word(seg)
    if cmd in _COPY_CMDS:
        # F-10-1（round11 建支，F-12-1/2 round13 三分句重构）：PS 复制族命名目标
        # 判定，全部按**本 cmd 目标标志绑定**（_PS_TARGET_FLAGS 分表，禁全局并集）：
        # 句1 本 token 判写 = before 尾锚本 cmd 目标标志 或 raw=冒号绑定本 token 为
        #   目标值，且段内该族标志未绑定**另一个**值（前随/后随段无第二次绑定）；
        # 句2 本 token 判读 = 段内本 cmd 目标标志已绑另一值 → PASS 且否决末位启发
        #   （X1~4 的 -Path/-Container/-LiteralPath 源参不接管目标；Z1/Z3 双绑必败
        #   形 pwsh 活证零写，规则天然导出，无特判——r10 B 锁形 K2 同此）。
        # 句3 段内本 cmd 无目标标志绑定 = 走末位启发（POSIX 位置参形，子句 3 同步
        #   per-cmd 目标尾锚语义——规格 A3：标志绑定的是别人时 before 非本尾锚）。
        # _PS_NAMED_ANY_RE 五词表仅作"命名标志在场"前置（规格 A4，不动）。
        named = cmd in ("copy-item", "tee-object") and _PS_NAMED_ANY_RE.search(seg)
        anch = _PS_TAIL_ANCHOR_RES.get(cmd)
        bind = _PS_TGT_BIND_RES.get(cmd)
        gl = _PS_GLUED_NAMED_RES.get(cmd)
        own = anch.search(before) if anch else None
        own_gl = bool(gl.match(raw)) if gl else False
        if named and (own or own_gl) \
                and not bind.search(seg[:own.start()] if own else seg[:m.start()]) \
                and not bind.search(seg[m.end():]):
            return True
        path_tokens = [t for t in _PATH_TOKEN_RE.finditer(seg)]
        if path_tokens and path_tokens[-1].start() == m.start() \
                and (not named or (own
                        and not bind.search(seg[:own.start()])
                        and not bind.search(seg[m.end():]))):
            # H-1：末位参数为 home 内**目录**形态（原始 token 以分隔符结尾）→ 写目标。
            # `cp evil.py <home>/plugins/write-guard/` 归一化后不等于任何受保护文件，
            # 但落盘语义=目录内同名覆写（守卫源码经 terminal 单命令可缴械）。
            if raw.rstrip("\"'").endswith(("/", chr(92))) \
                    and norm is not None and norm.startswith(_hermes_home() + _SEP):
                return True
            # F-1：目标是守卫插件目录（无尾分隔符的 Windows 同义形态）→ 写
            if _is_guard_dir_target(norm):
                return True
            return True                   # 末位路径参数 = 复制目标
        # cp -t <dir> src…：当前路径参数是受保护目录本身（home）或其内目录，
        # 且带 -t 目标标志 → 写面（安全走查 F-A7）。
        home = _hermes_home()
        # H-1：-t 目标可为 home 本身或 home 内任意目录（原仅 == home 太窄）
        # F-1：-t 目标同样接受守卫目录无分隔符形态
        # R4-1（round4）：仅 cp/install 的 -t 是"目标目录"标志；rsync 的 -t 是
        # preserve-times（选项语义不同），按 cp 套用过拦纯读形态 rsync -t <CFG> dest/。
        if (cmd in ("cp", "install") and norm is not None
                and (norm == home or norm.startswith(home + _SEP)
                     or _is_guard_dir_target(norm))
                and (_COPY_T_RE.search(before)
                     # F-13-S1-A2（round14）：--target-directory= 前缀支匹配输入接
                     # _pair_unquote（仅判定视图，`cp "--target-directory=<CFG>"`
                     # 与裸形同义；norm 链不经过——F-7-2 禁令）
                     or _pair_unquote(raw).lower().startswith("--target-directory=")
                     # Q-6-1：本 token 即粘连目标形；F-13-S1-A1（round14）匹配输入
                     # 接 _pair_unquote（cp x "-t<DIR>" 引号整包，含守卫缴械形）
                     or _GLUED_T_RE.match(_pair_unquote(raw))
                     or _COPY_T_QUOTED_RE.search(before))):  # 引号选项形
            return True
        return False
    if cmd in _MOVE_CMDS:
        return False                       # 路径级操作（OOS-09）不拦
    # truncate 置零目标文件 → 写（安全走查 F-A5）
    if cmd == "truncate":
        return True
    # pwsh/cmd 包裹下的 Set-Content/Add-Content/Out-File → 写（F-A6）
    if _PS_WRITE_RE.search(before):
        return True
    return False


def _split_shell(text, seps):
    """按引号外的分隔符切分 shell 文本（质量审查 R-1）。
    规则与 shell 语义对齐：单引号内全字面；双引号内 \\ 转义有效；
    引号外 \\x 为转义字面量。seps 按长度降序传入（'||' 先于 '|' 匹配）。
    返回 strip 后的非空片段列表。无法配平引号（奇数引号）时不切分——
    保守返回整体，由下游 token 级判定兜底（引号未闭合的命令本身异常形态）。"""
    quote = None
    out, buf, i, n = [], [], 0, len(text)
    while i < n:
        ch = text[i]
        if quote == "'":
            buf.append(ch)
            if ch == "'":
                quote = None
            i += 1
        elif quote == '"':
            if ch == "\\" and i + 1 < n:
                buf.append(ch); buf.append(text[i + 1]); i += 2
            else:
                buf.append(ch)
                if ch == '"':
                    quote = None
                i += 1
        elif ch == "\\" and i + 1 < n:
            buf.append(ch); buf.append(text[i + 1]); i += 2
        elif ch in ("'", '"'):
            quote = ch
            buf.append(ch)
            i += 1
        else:
            for sep in seps:
                if text.startswith(sep, i):
                    out.append("".join(buf))
                    buf = []
                    i += len(sep)
                    break
            else:
                buf.append(ch)
                i += 1
    if quote is not None:
        return [text]                     # 引号不配平：不切分，整体交下游
    out.append("".join(buf))
    return [s for s in (x.strip() for x in out) if s]


def _join_line_continuations(text):
    """F-7-1（round8）：引号感知续行粘连（取代 _judge_terminal 入口盲 replace——
    盲替换把成对反斜杠后的真换行也误当续行合并、且不认引号态，转义反斜杠形
    `echo a<2bs>LF cp evil <guard>` 两段被误并成一段=旁路）。引号外 反斜杠+LF
    （含反斜杠+CRLF）=shell 续行 → 删两（三）字符、行直接相接；单引号内字面
    不处理；双引号内不处理——按 2026-09-22 范围决策排除第 2 条登记接受边界，
    TC 锁现状。反斜杠逐对消耗，自然满足「成对不粘连、奇数末位单斜杠为字面」。"""
    NL, CR, BS, SQ, DQ = chr(10), chr(13), chr(92), chr(39), chr(34)
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


def _judge_terminal(command, tool_name, depth=0, base_cwd=None):
    """terminal 写命令判定（DR-09 / 3.2.2）：先按管道分段（LOW-1）、段内再按
    （&& / ;）分段 + cd 链静态跟踪。管道两侧环境独立（设计 3.2.2：管道左侧
    cd 运行在子进程，不跨管道传播），cd 只在其所在管道段内生效；cd 目标无法
    静态解析（残留环境变量引用等）→ 整条命令立即放行（Q-03，LOW-2）。"""
    if not isinstance(command, str) or not command.strip():
        return None
    cwd = base_cwd or os.getcwd()
    # R-1：引号感知分段（取代裸 re.split——引号内的 ; 与 | 不是分隔符）；
    # LOW-1 语义保持：先管道级、cd 不跨管道传播
    # NL（round6 sa-0 D 卷实锤）：换行=shell 命令分隔符，此前分段集不含换行，
    # ls+换行+cp evil <guard> 整段不命中=反缴械旁路。修法（复审侧 r6_d 仿真
    # 验证）：反斜杠+换行=续行，引号感知状态机删字符直接相接（round8 F-7-1 重写，禁盲 replace）；再按换行分段（引号内换行由
    # _split_shell 引号感知保持不切——heredoc/引号负例/既有链零回潮）。
    command = _join_line_continuations(command)  # F-7-1（round8）引号感知粘连
    for pipe_seg in _split_shell(command, ("||", "|")):
        pipe_seg = pipe_seg.strip()
        if not pipe_seg:
            continue
        pipe_cwd = cwd                       # 管道两侧独立：cd 不跨管道传播
        # S-3（round9 fix-009）：追加单 &（cmd 链式分隔；&&/|| 已按长度降序先行消费，
        # _split_shell 引号感知——URL 内 & 不误切）
        for seg in _split_shell(pipe_seg, ("&&", "||", ";", "\n", "\r", "&")):
            seg = seg.strip()
            if not seg:
                continue
            m = _CD_PREFIX_RE.match(seg)
            if m:
                target = m.group(1).strip().strip('"').strip("'")
                # LOW-2：cd 目标展开后仍残留环境变量引用形态（如 $VAR 未定义）
                # → 无法静态解析 → 按设计语义（DR-09 / Q-03）整条命令立即放行，
                # 不污染后续段判定（不得拼接进 cwd 继续判定）
                if _ENV_REF_RE.search(_expand_env(target)):
                    return None
                new_cwd = _normalize_path(target, base=pipe_cwd)
                if new_cwd is None:
                    return None              # cd 目标无法静态解析 → 放行（Q-03）
                pipe_cwd = new_cwd
                continue
            hit = _judge_terminal_segment(seg, pipe_cwd, tool_name, depth)
            if hit is not None:
                return hit
    return None


def _config_write_disposition(tool_name, cmd_word, raw, norm):
    """A 项配置写处置（用户决策 2026-09-21）：
    - 复制类命令（cp/copy/install 目标 / shutil.copy 目标）写配置 → approve（弹卡）
      —— 用户明确：cp 是改配置文件的方法，保留审批通道；
    - 其他一切写配置方法（echo >/tee/sed -i/curl -o/execute_code open('w')
      等）→ block（直接截断，必须走 safe-config-modify skill 流程）。
    """
    if cmd_word in _COPY_CMDS:
        return _approve_result(tool_name, raw, norm)
    return _config_block_result(tool_name, raw, norm)


def _judge_terminal_segment(seg: str, cwd: str, tool_name: str, depth=0):
    """对单个命令段判定：先按内嵌脚本写调用（3.2.2 矩阵末行）扫描，
    再枚举受保护路径 token 按写语义矩阵判定。"""
    hit = _judge_execute_code(seg, tool_name, base=cwd, depth=depth)
    if hit is not None:
        return hit
    # M-1：内嵌 shell 载体段（bash -c "…" / pwsh -Command "…" / cmd /c "…"）——
    # 引号体是完整 shell 命令，递归按 terminal 链判定（深度上限防互爆）。
    # F-9-2（round10）：匹配对象改用 wrapper 剔除链输出的剩余文本（单点改在
    # 载体识别入口；无 wrapper 前导时 _strip_wrapper_prefix 原样返回，零行为差）。
    if depth < _NEST_DEPTH_LIMIT:
        carrier_seg = _strip_wrapper_prefix(seg)
        em = _EMBED_SHELL_RE.search(carrier_seg)
        if em is not None:
            hit = _judge_terminal(em.group("body"), tool_name,
                                  depth=depth + 1, base_cwd=cwd)
            if hit is not None:
                return hit
        # S-5（round9 fix-009）：载体裸形剥词递归——cmd /c copy … 无引号体时，
        # 剥载体词与开关位，剩余文本 depth+1 复用同一 terminal 链判定。
        bm = _BARE_CARRIER_RE.match(carrier_seg)
        if bm is not None and bm.group("rest").strip() and _EMBED_SHELL_RE.search(carrier_seg) is None:
            hit = _judge_terminal(bm.group("rest"), tool_name,
                                  depth=depth + 1, base_cwd=cwd)
            if hit is not None:
                return hit
    protected = []
    for m in _PATH_TOKEN_RE.finditer(seg):
        raw = m.group(0)
        # MED-2：= 粘连的输出标志形态（curl --output=路径 等）提取真实路径。
        # F-13-S1（round14）：仅**前缀提取支**（eq/of=/--target-directory=/=粘连形）
        # 的匹配输入改剥对引号视图 _raw_ou——剥后内容本身不再带外层引号，norm 的
        # 剥壳结果逐字节不变（token 化仍走 raw，F-7-2 禁令不回潮）。
        _raw_ou = _pair_unquote(raw)
        eq_m = _OUTPUT_FLAG_EQ_RE.match(_raw_ou)
        if eq_m:
            norm_raw = eq_m.group(1)
        elif _raw_ou.lower().startswith("of="):
            norm_raw = _raw_ou[3:]
        elif _raw_ou.lower().startswith("--target-directory="):
            norm_raw = _raw_ou.split("=", 1)[1]   # C3：cp --target-directory=<dir> 粘连
        elif _raw_ou.startswith("=") and _COPY_T_QUOTED_RE.search(seg[:m.start()]):
            # F-7-2（round8 灰区判=两行可修则做）：引号选项词后紧跟 = 粘连形
            # cp "--target-directory"=<dir>——本 token 值即 = 后路径（选项词在
            # 前一 token；判定仍由 -t 分支 _COPY_T_QUOTED_RE 门把关，保守收集）。
            norm_raw = _raw_ou[1:]
        else:
            # F-12-3（round13）：_GLUED_O_RE 匹配输入剥**成对**外层引号一处（比照
            # _GLUED_T_RE 引号先例语义）——引号吞选项粘连值形 `curl "-so<CFG>"` 与
            # 裸形同义（shell 剥引号实证）；token 化与 norm 链不经过此（F-7-2 禁令）。
            # 复制族 cmd 不启用：-o 非其选项语义，零扰动。
            # F-13-S1-A1（round14）：_GLUED_T_RE 匹配输入同步接 _pair_unquote——
            # 粘连入口全族同法（-o 族 r13 已接、-t 族本轮补齐，覆盖不对称教训固化句
            # 见 CHANGELOG round14）；复制族门后，token 化/norm 链不经过。
            cmdw = _command_word(seg)
            _ou = raw if cmdw in _COPY_CMDS else _pair_unquote(raw)
            gm = _GLUED_T_RE.match(_pair_unquote(raw)) or _GLUED_O_RE.match(_ou)   # Q-6-1：-t<dir> / S-1：-o<file> 粘连短形
            # F-11-1（round12）建支，round13 per-cmd 化：冒号粘连值段按本 cmd 目标
            # 词表匹配（引号优先于 t/o 误提取）——非本 cmd 目标族标志不提取。
            gn = _PS_GLUED_NAMED_RES.get(cmdw)
            gn = gn.match(raw) if gn else None
            norm_raw = gn.group(2) if gn else (gm.group(1) if gm else raw)
        norm = _normalize_path(norm_raw, base=cwd)
        if norm is None:
            continue
        # terminal 面额外收集 HERMES_HOME 目录本身：`cp x <home>/` 的目标是
        # 目录（写入落为目录内同名文件）——写矩阵各分支只对真写形态返回
        # True，读命令（cat/grep/ls <home>/）经矩阵判定仍放行（F-A7）。
        is_dir_target = (raw.rstrip("\"'").endswith(("/", chr(92)))
                         and norm is not None
                         and (norm == _hermes_home() or norm.startswith(_hermes_home() + _SEP)))
        # F-1：收集面同步放宽——守卫目录 token（无尾分隔符）也进写矩阵判定，
        # 读命令（cat/ls 该目录）由矩阵按读语义放行，不受收集面影响。
        if not is_dir_target and _is_guard_dir_target(norm):
            is_dir_target = True
        if not is_dir_target \
                and norm.startswith(_hermes_home() + _SEP) \
                and norm != _hermes_home() \
                and _command_word(seg) in _COPY_CMDS:
            # C4（round5 sa-0）：cp x <home>/profiles/developer（无尾分隔符，
            # Windows/GNU 目标为目录时可省）落盘=目录内同名覆写。收集进矩阵，
            # 由既有"末位路径参数=复制目标"分支按 approve 处置（读命令与
            # 末位非本 token 形态矩阵自会放行）。
            # Q-6-3 名实补记：静态无法辨目录/文件属性，实收 home 内任意末位
            # token（含普通文件）——文件末位=覆写该文件本就应审批，保守方向。
            ptoks = list(_PATH_TOKEN_RE.finditer(seg))
            if ptoks and ptoks[-1].start() == m.start():
                is_dir_target = True
        if _is_protected_config(norm) or norm == _hermes_home() or is_dir_target:
            protected.append((m, raw, norm))
    if not protected:
        return None
    for m, raw, norm in protected:
        if _terminal_position_is_write(seg, m, raw, norm, cwd):
            cmd_word = _command_word(seg)
            return _config_write_disposition(tool_name, cmd_word, raw, norm)
    return None


def _call_content(text: str, start: int) -> str:
    """从 '(' 开始括号配对，返回括号内内容（os.open 标志判定用）。"""
    depth = 0
    for i in range(start, len(text)):
        c = text[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[start + 1:i]
    return text[start:]


def _judge_execute_code(code, tool_name, base=None, depth=0):
    """execute_code 写形态启发式（DR-10 / 3.2.3）：写模式打开 / 路径对象写方法 /
    复制至目标 / 底层写标志 / 代码内工具调用为写；读模式、路径级操作、动态变量、
    r+ 混合模式放行（Q-03）。提取出的转义字面量实参先解义再归一化（DR-22）。

    用户决策（2026-09-21）：shutil.copy 目标（等效 cp）→
    approve；其余写配置形态 → block（直接截断）。"""
    if not isinstance(code, str) or not code.strip():
        return None
    # N-3：三引号字面量折叠为单引号后再判定（open(三引号x三引号) 与 open('x')
    # 判定语义相同；一处归一替代 6 条正则各自支持三引号的复杂度）。仅影响
    # 判定视图（本函数纯判定无副作用，不回写执行内容）。
    _tri_dq = chr(34) * 3
    if chr(39) * 3 in code or _tri_dq in code:
        code = code.replace(chr(39) * 3, chr(39)).replace(_tri_dq, chr(34))
    # 内嵌 shell 面（安全走查 F-A2）：execute_code 里 os.system/popen、
    # subprocess.* 携带的 shell 命令文本，复用 terminal 判定链（含写矩阵与
    # 处置分流）——execute_code 不得成为 terminal 防线之外的旁路写入口。
    # depth 防 terminal↔execute_code 互递归爆栈（_NEST_DEPTH_LIMIT）。
    if depth < _NEST_DEPTH_LIMIT:
        for m in _OS_SYSTEM_RE.finditer(code):
            hit = _judge_terminal(m.group("cmd"), tool_name,
                                  depth=depth + 1, base_cwd=base)
            if hit is not None:
                return hit
        # 执行点集合：subprocess.xxx(...) 限定形 + （存在 from-import 时）裸词形
        call_sites = [(m.start(), m.end()) for m in _SUBPROC_CALL_RE.finditer(code)]
        # F-3 模块别名形：`import subprocess as sp` → sp.run(...) 等限定调用
        for im in _SUBPROC_IMPORTED_RE.finditer(code):
            alias = im.group(3)
            if alias:
                alias_re = re.compile(
                    r"\b" + re.escape(alias) + r"\.\w+\s*\(")
                call_sites += [(x.start(), x.end()) for x in alias_re.finditer(code)]
        # N-1 from-import 门：仅当代码确实把 subprocess 函数导入成裸名时才扫裸词
        # （防误拦业务 run()）。F-3 扩展门条件：别名 as r、star import *、多行括号。
        bare_names, star = [], False
        for im in _SUBPROC_IMPORTED_RE.finditer(code):
            body = im.group(1) if im.group(1) is not None else (im.group(2) or "")
            if "*" in body:
                star = True
            toks = body.replace(",", " ").split()
            i = 0
            while i < len(toks):
                name, alias = toks[i], None
                if i + 2 < len(toks) and toks[i + 1] == "as":
                    alias = toks[i + 2]        # `run as r`：生效名是别名 r
                    i += 3
                else:
                    i += 1
                if name in _SUBPROC_FUNCS:
                    bare_names.append(alias or name)
        if star:
            bare_names = list(_SUBPROC_FUNCS)
        for fn in bare_names:
            bare = re.compile(r"\b" + re.escape(fn) + r"\s*\(")
            for bm in bare.finditer(code):
                pre = code[:bm.start()].rstrip()
                if pre.endswith(".") or pre.endswith("as"):
                    continue          # 限定形已收集 / `import x as run` 声明本身
                call_sites.append((bm.start(), bm.end()))
        for cstart, cend in call_sites:
            call_open = code.find("(", cstart)
            if call_open == -1:
                continue
            content = _call_content(code, call_open)
            # 字符串字面量（单串命令或 list 逐项）拼为命令文本；参数结构近似
            # 空格连接，cp 目标位等语义得以保留（安全走查 t2 A-B2b 教训）。
            cmd_text = " ".join(mm.group(2) for mm in _STR_LIT_RE.finditer(content))
            if cmd_text:
                hit = _judge_terminal(cmd_text, tool_name,
                                      depth=depth + 1, base_cwd=base)
                if hit is not None:
                    return hit
    hits = []

    def record(pos, raw, norm, kind):
        if norm is not None and _is_protected_config(norm):
            hits.append((pos, raw, norm, kind))

    for m in _OPEN_WRITE_RE.finditer(code):
        if _OPEN_WAX_RE.search(m.group("mode")):       # 写/追加/排他创建模式
            record(m.start(), m.group("path"), _normalize_path(m.group("path"), base=base), "open")
    for m in _PATH_WRITE_RE.finditer(code):
        record(m.start(), m.group(2), _normalize_path(m.group(2), base=base), "path_write")
    for m in _PATH_OPEN_RE.finditer(code):
        if _OPEN_WAX_RE.search(m.group(4)):
            record(m.start(), m.group(2), _normalize_path(m.group(2), base=base), "path_open")
    for m in _SHUTIL_COPY_RE.finditer(code):           # 目标参数为写方向；源为读
        record(m.start(), m.group(4), _normalize_path(m.group(4), base=base), "copy")
    for m in _OS_OPEN_RE.finditer(code):
        # _OS_OPEN_RE 的匹配止于路径右引号，故写标志需自行配对括号提取
        # （DR-10 / 3.2.3「底层打开写标志」形态）；定位失败即跳过该命中。
        open_paren = code.find("(", m.start())
        if open_paren == -1:
            continue
        content = _call_content(code, open_paren)
        if any(flag in content for flag in _OS_WRITE_FLAGS):
            record(m.start(), m.group(2), _normalize_path(m.group(2), base=base), "os_open")
    for m in _TOOL_CALL_PATH_RE.finditer(code):
        p = m.group("p1") if m.group("p1") is not None else m.group("p2")
        record(m.start(), p, _normalize_path(p, base=base), "tool_call")
    if not hits:
        return None
    hits.sort(key=lambda t: t[0])                      # 代码顺序第一个命中
    _, raw, norm, kind = hits[0]
    if kind == "copy":                                 # shutil.copy 目标 = cp 等效 → approve
        return _approve_result(tool_name, raw, norm)
    return _config_block_result(tool_name, raw, norm)   # 其余写配置形态 → block


# =====================================================================
# ④ 守卫实现区（CON-02：三拦截项各自独立函数，禁止混写）
# =====================================================================

def _guard_hermes_config(tool_name: str, args: dict, task_id: str = "") -> dict | None:
    """守卫 A：Hermes 配置写保护（FR-01~06）。只识别 _CONFIG_SCAN_TOOLS 四工具
    （DR-08），其他工具不扫描直接放行。
    M-3：terminal 显式 workdir 参数作为相对路径判定基准（对齐平台 per-command
    cwd 语义），缺省回退进程 cwd。"""
    if tool_name not in _CONFIG_SCAN_TOOLS:
        return None
    # S-3：参数名取自 _TOOL_ARG_MAP 单一来源（DR-08 覆盖集 + 映射键由 TC-X-10
    # 不变量锁定 ⊆ 关系），新增工具只改两处常量、判定分支按 kind 路由。
    arg_name = _TOOL_ARG_MAP[tool_name][0]
    text = args.get(arg_name)
    if tool_name in ("write_file", "patch"):
        return _judge_path_param(text, tool_name)
    if tool_name == "terminal":
        # M-3：显式 workdir 优先为判定基准（与平台 _resolve_command_cwd 一致）。
        # F-2（round4 MED）：平台把 workdir 原样传 shell，相对形态由 shell 相对
        # **会话 cwd** 解析（`workdir="../.hermes"` 实际落盘 home）——判定时先按
        # 进程 cwd 绝对化，与 shell 会话 cwd=进程 cwd 的常态一致（会话 cd 漂移
        # 是 M-3 已登记的接受边界，此处不再叠加）。
        wd = args.get("workdir")
        base = None
        if isinstance(wd, str) and wd.strip():
            base = _normalize_path(wd)
        return _judge_terminal(text, tool_name, base_cwd=base)
    if tool_name == "execute_code":
        return _judge_execute_code(text, tool_name)
    return None   # S-5 显式兜底：已声明进扫描集但无判定分支的工具按未命中放行


def _guard_memory_write(tool_name: str, args: dict, task_id: str = "") -> dict | None:
    """守卫 B：记忆写保护（FR-07~09）。按工具名精确匹配（DR-13），不分析 args、
    不审查记忆内容（OOS-05）；查询工具不在清单自然放行（FR-08）。"""
    if tool_name in _MEMORY_WRITE_TOOLS:
        logger.warning(
            "write-guard: 拦截 %s（task=%s）— 记忆写需人工审批", tool_name, task_id)
        return {
            "action": "approve",
            "message": _MEMORY_APPROVE_TEMPLATE.format(tool_name=tool_name),
            "rule_key": f"write_guard:memory:{tool_name}",
        }
    return None


# =====================================================================
# ⑤ 调度器与入口区（FR-12 / FR-13 / FR-14 / DR-02 / DR-15）
# =====================================================================

# D 守卫扫描面（S-3：命令执行类工具的「命令文本参数」集中声明；与
# _TOOL_ARG_MAP 的 command/code 一致，单独成表避免 kind 语义耦合）
_GATEWAY_SCAN_ARGS = {"terminal": "command", "execute_code": "code"}

# 守卫 D 禁令匹配（用户决策 2026-09-21）：hermes 与 gateway 之间允许全局
# flag（hermes -p dev gateway restart），不允许跨命令分隔符（;&|换行）误连；
# 动词仅限 restart/run/start（status/stop 不在禁令内）。
_GATEWAY_BANNED_RE = re.compile(
    r"\bhermes\b[^\n;&|]*?\bgateway\b[^\n;&|]*?\b(restart|run|start)\b",
    re.IGNORECASE,
)
_GATEWAY_BANNED_MESSAGE = "你违反了用户的规则, 必须使用skill指定的方式来访问hermes gateway"

# 固定轮询顺序 [D, C, A, B]（Q-01 用户决策 + 2026-09-21 用户禁令新增 D）：
# D gateway 命令禁令最前（轻量精确正则、独立于其余守卫），C 临时目录拦截次之，
# A 配置写保护，B 记忆写保护最后。C 结构性排在 A/B 之前，保证 A/B 任何异常或
# 改动都无法旁路 C。

def _guard_gateway_cmd(tool_name: str, args: dict, task_id: str = "") -> dict | None:
    """守卫 D：Gateway 生命周期命令禁令（用户决策 2026-09-21）。
    `hermes gateway restart|run|start` 一律 block——gateway 启停必须走
    gateway-restart skill 背书的固定命令（gateway-restart.ps1），禁止直接
    CLI；status 查询与 stop 不在本次禁令范围（stop 走 skill 的同一脚本）。
    扫描范围：terminal command / execute_code code 两个参数（命令执行面）。
    防呆层定位（非防恶意）：覆盖直写与全局 flag 形态（hermes -p x gateway
    restart）、反斜杠续行、大小写；变量拼接/base64 等刻意混淆不在范围。"""
    arg_name = _GATEWAY_SCAN_ARGS.get(tool_name)   # S-3：参数名集中声明
    if arg_name is None:
        return None
    text = args.get(arg_name)
    if not isinstance(text, str) or not text:
        return None
    # 反斜杠续行归一（`hermes gateway \<nl>restart` 实际是一条命令）
    text = _join_line_continuations(text)   # F-7-1 同源：CRLF 续行一并封（红线 block 保持）
    m = _GATEWAY_BANNED_RE.search(text)
    if m:
        logger.warning(
            "write-guard: 拦截 %s（task=%s）— 禁用 hermes gateway %s",
            tool_name, task_id, m.group(1).lower(),
        )
        return {
            "action": "block",
            "message": _GATEWAY_BANNED_MESSAGE,
        }
    return None


GUARDS = [
    _guard_gateway_cmd,     # D：Gateway 生命周期命令禁令（2026-09-21 用户决策）
    _guard_tmpdir,          # C：临时目录拦截
    _guard_hermes_config,   # A：配置写保护
    _guard_memory_write,    # B：记忆写保护
]


def on_pre_tool_call(tool_name, args, task_id="", **kwargs):
    """唯一入口：按固定顺序 [D, C, A, B] 轮询各守卫，命中即返，全部未命中放行。
    项级 try/except 异常隔离（FR-14）：任一守卫抛异常 → 记日志后按未命中处理、
    继续轮询后续守卫，插件不整体失效（不得依赖平台 hook 异常兜底，平台行为
    为整个 hook 返回放行）。"""
    if not isinstance(args, dict):
        # F-7（round4）：args 非 dict（None/str/调用方畸形）时三守卫都会抛
        # AttributeError 并被项级隔离逐个吞掉 → 整链放行（fail-open 残面）。
        # 入口收敛：按空参数走完整守卫链（各守卫对缺参自有保守路径）。
        args = {}
    try:
        for guard in GUARDS:
            try:
                result = guard(tool_name, args, task_id)
            except Exception:
                # FR-14：项级异常隔离——记日志后按未命中处理，继续轮询后续守卫
                logger.exception(
                    "write-guard: 守卫 %s 抛出异常，按未命中处理，继续轮询（task=%s）",
                    guard.__name__, task_id,
                )
                continue
            if result is not None:
                logger.info(
                    "write-guard: 守卫 %s 命中（task=%s），返回 action=%s",
                    guard.__name__, task_id, result.get("action"),
                )
                return result
        return None
    except Exception:
        # DR-15：调度器外层防御性兜底（正常不应发生，见 5.3 语义说明）
        logger.exception("write-guard: 调度器整体异常，按放行处理（防御性兜底）")
        return None
