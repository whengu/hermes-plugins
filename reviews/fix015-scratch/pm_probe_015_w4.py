# PM round15 在途挖洞探针（只读 judge，1 字符收窄第三维邻域差分）
import importlib.util, os
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
spec = importlib.util.spec_from_file_location("p15", W := r"D:\myagent\workspace\write-guard" + B + "handler.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
CFG = "D:" + B + "myagent" + B + ".hermes" + B + "config.yaml"
def call(cmd):
    r = m.on_pre_tool_call("terminal", {"command": cmd}, "pm")
    return "PASS" if r is None else str(r.get("action"))

# 收窄第三维邻域：dash 必选后的边界组合面
cases = [
    ('curl "-" CFG 纯dash单字符',        f'curl "-" {CFG}',                      "any"),
    ('curl "--" CFG 双dash',             f'curl "--" {CFG}',                     "any"),
    ('curl "" CFG 空串引号',             f'curl "" {CFG}',                       "pass"),
    ('curl "-O" CFG 大写保 r12 锁',       f'curl "-O" {CFG}',                     "hit"),
    ('curl "-o" CFG 小写保 r12 锁',       f'curl "-o" {CFG}',                     "hit"),
    ('curl "-oO" CFG 尾o复字母',          f'curl "-oO" {CFG}',                    "hit"),
    ('curl "-0o" CFG 数字夹',            f'curl "-0o" {CFG}',                    "any"),
    ('curl \'-so\' 单引号 cluster',       f"curl '-so' {CFG}",                    "hit"),
    ('sort "-o" CFG 门内',               f'sort "-o" {CFG}',                     "hit"),
    ('grep "-so" 门外零误拦',            f'grep "-so" {CFG}',                    "pass"),
    ('curl "-o" 非保护 零误拦',           'curl "-o" out.txt',                   "pass"),
    ('curl "Cairo" CFG r15靶心保持',      f'curl "Cairo" {CFG}',                  "pass"),
    ('sort "logo" CFG d r15靶心保持',     f'sort "logo" {CFG} d.txt',             "pass"),
    ('wget "--output-document=x" 长形',   f'wget "--output-document={CFG}" http://x', "hit"),
    # 共用位点牵连检查：-t 族/of= 不受本批影响（round14 已修形保持）
    ('cp "-t<CFG>" r14 形不回潮',         f'cp f "-t{CFG}"',                      "hit"),
    ('dd "of=<CFG>" r14 形不回潮',        f'dd "of={CFG}" if=x',                  "hit"),
]
nb = 0
for label, cmd, want in cases:
    got = call(cmd)
    okv = {"hit": got in ("approve", "block"), "pass": got == "PASS", "any": True}[want]
    nb += (not okv)
    print(f"{'ok ' if okv else 'FAIL'} {label:36s} -> {got}")
print(f"wave4 {len(cases)} 形: 符合预期 {len(cases)-nb}, 异常 {nb}")
