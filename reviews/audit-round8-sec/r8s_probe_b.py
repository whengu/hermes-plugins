# round8 安全路探针 B：token 语义追踪 + dd/引号、空格变体、.exe 后缀、cmdlet 族
import importlib.util, os, sys
spec = importlib.util.spec_from_file_location("hg", "handler.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
CFG = "D:/myagent/.hermes/config.yaml"
GUARD = "D:/myagent/.hermes/plugins/write-guard"

print("PATH_TOKEN_RE pattern repr:", repr(h._PATH_TOKEN_RE.pattern))

def term(cmd):
    r = h.on_pre_tool_call("terminal", {"command": cmd})
    return (r or {}).get("action", "PASS")

def trace_seg(cmd):
    print("TRACE", repr(cmd))
    j = h._join_line_continuations(cmd)
    for seg in h._split_shell(j, ("&&", "||", ";", "\n", "\r")):
        toks = [t.group(0) for t in h._PATH_TOKEN_RE.finditer(seg)]
        print("  seg:", repr(seg))
        print("  tokens:", toks)
        for t in toks:
            print("    norm", repr(t), "->", h._normalize_path(t))
        print("  judge:", term(cmd))

trace_seg("echo x >D:/myagent/.hermes/config.yaml")   # 有空格 >粘连
trace_seg("echo x>D:/myagent/.hermes/config.yaml")    # 无空格
trace_seg("echo x >>D:/myagent/.hermes/config.yaml")  # >> 粘连
run = lambda group, cases: [print(f"[{term(c):7s}] {c!r}") for c in cases] or print(group)

run("dd of quoted", [
    'dd of="D:\\myagent\\.hermes\\config.yaml" if=/dev/zero',
    "dd of='" + CFG + "' if=/dev/zero",
    'dd if=x of="' + CFG + '"',
])
run("exe suffix", [
    "cp.exe evil " + GUARD,
    "Copy.exe evil " + GUARD,
    "curl.exe -o " + CFG + " http://x",
    "sed.exe -i s/a/b/ " + CFG,
])
run("cmdlets", [
    "Copy-Item evil " + CFG,
    "Copy-Item -Path evil -Destination " + CFG,
    "Tee-Object -FilePath " + CFG,
    "cmd /c Copy-Item evil " + CFG,
    "pwsh -Command Copy-Item evil " + CFG,
    "pwsh -Command \"Copy-Item evil " + CFG + "\"",
])
run("case forms (§6)", [
    "CP evil " + GUARD,
    "cP evil D:/MyAgent/.HERMES/Plugins/Write-Guard",
    "install -t " + CFG.rsplit("/", 1)[0] + " evil",
])
run("misc targets", [
    "echo x > %HERMES_HOME%\\config.yaml",
    "echo x > $env:HERMES_HOME/config.yaml",
    "cd D:/myagent && echo x > .hermes/config.yaml",
    "cp evil \"\\\\\\\\?\\\\D:\\myagent\\.hermes\\config.yaml\"",
    "truncate -s 0 " + CFG,
])
