# PM round13 在途挖洞探针（只读 judge 差分，新邻域形，禁入 pm_verify_013 既有 30 形）
# 邻域：载体递归×per-cmd 新表 / 双绑天然导出 / 大写 cmdlet / 误拦反向面
import importlib.util, os
B = chr(92)
os.environ["HERMES_HOME"] = "D:" + B + "myagent" + B + ".hermes"
os.chdir("D:" + B + "myagent" + B + "workspace")
W = r"D:\myagent\workspace\write-guard"
spec = importlib.util.spec_from_file_location("w...er", W + B + "handler.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

CFG = "D:" + B + "myagent" + B + ".hermes" + B + "config.yaml"
GRD = "D:" + B + "myagent" + B + ".hermes" + B + "plugins" + B + "write-guard" + B + "handler.py"
WS  = "D:" + B + "myagent" + B + "workspace" + B + "ok.txt"

def call(cmd):
    r = m.on_pre_tool_call("terminal", {"command": cmd}, "probe")
    return "PASS" if r is None else str(r.get("action"))

cases = [
    # -- 载体递归 × 新 per-cmd 表（期望全部命中，不得 PASS）
    ("R-A pwsh -Cmd Copy-Item -Dest CFG -Path WS",
     'pwsh -NoProfile -Command "Copy-Item -Destination ' + CFG + ' -Path ' + WS + '"', "hit"),
    ("R-B pwsh -Cmd Tee -LiteralPath CFG",
     'pwsh -NoProfile -Command "Tee-Object -LiteralPath ' + CFG + '"', "hit"),
    ("R-C pwsh -Cmd Tee -LiteralPath GRD(反缴械)",
     'pwsh -NoProfile -Command "Tee-Object -LiteralPath ' + GRD + '"', "hit"),
    ("R-D pwsh 分号链 后段写 CFG",
     'pwsh -NoProfile -Command "Get-Process; Copy-Item -Destination ' + CFG + ' -Path ' + WS + '"', "hit"),
    # -- 双绑必败形（pwsh 绑定错误零写，规则应天然导出，Z 组同族新形）
    ("Z4 Tee -LiteralPath WS -FilePath CFG 双绑",
     'Tee-Object -LiteralPath ' + WS + ' -FilePath ' + CFG, "any"),
    ("Z5 Tee -FilePath CFG -LiteralPath WS 双绑反序",
     'Tee-Object -FilePath ' + CFG + ' -LiteralPath ' + WS, "any"),
    ("Z6 Copy -Dest CFG 后随 -Destination:WS 混粘",
     'Copy-Item -Destination ' + CFG + ' -Destination:' + WS, "any"),
    # -- 大小写 cmdlet / 大小写标志（key 归一化邻域）
    ("U-A COPY-ITEM -DESTINATION CFG -Path WS",
     'COPY-ITEM -DESTINATION ' + CFG + ' -Path ' + WS, "hit"),
    ("U-B copy-item -destination CFG (全小写)",
     'copy-item -destination ' + CFG + ' -Path ' + WS, "hit"),
    ("U-C TEE-OBJECT -LITERALPATH CFG",
     'TEE-OBJECT -LITERALPATH ' + CFG, "hit"),
    ("U-D Copy-Item -DeStInAtIoN:CFG WS 混合大小写冒号",
     'Copy-Item -DeStInAtIoN:' + CFG + ' ' + WS, "hit"),
    # -- 误拦反向面（期望 PASS，不得命中）
    ("N-A Copy-Item CFG(源读) -Dest WS",
     'Copy-Item ' + CFG + ' -Destination ' + WS, "pass"),
    ("N-B Copy-Item -Path CFG -Destination WS",
     'Copy-Item -Path ' + CFG + ' -Destination ' + WS, "pass"),
    ("N-C curl \"-o<非保护>\" url 引号粘连误拦?",
     'curl "-oout.txt" http://x', "pass"),
    ("N-D Tee 管道读源 Set-Content WS | Tee -FilePath OK2",
     'Set-Content ' + WS + ' x | Tee-Object -FilePath ' + WS + "2", "pass"),
    ("N-E Write-Host -LiteralPath 字面 非cmdlet载体词",
     'Write-Host -Destination ' + CFG, "pass"),
    # -- 冒号/= 混合粘连新邻域（等号形 r13 附录不修，但冒号+等号双连？）
    ("E-X -Destination:=CFG 冒号等号连",
     'Copy-Item -Destination:=' + CFG + ' -Path ' + WS, "any"),
]

npass = 0
for label, cmd, want in cases:
    got = call(cmd)
    okv = {"hit": got in ("approve", "block"), "pass": got == "PASS", "any": True}[want]
    npass += okv
    flag = "ok " if okv else "FAIL"
    print(f"{flag} {label:52s} -> {got:8s} want {want}")
print(f"探针 {len(cases)} 形：符合预期 {npass}，异常 {len(cases)-npass}")
