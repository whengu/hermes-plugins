#!/usr/bin/env python3
"""write-guard 一键部署脚本（Windows / 跨平台）

用法: python deploy.py
作用: 将 workspace 源目录的核心文件同步到 Hermes 插件部署目录，
      清理旧字节码缓存，校验语法与一致性。
不拷贝测试文件（部署目录仅需要 __init__.py / handler.py / plugin.yaml）。
"""

import shutil
import subprocess
import sys
from pathlib import Path

SRC = Path(r"D:\myagent\workspace\write-guard")
DST = Path(r"D:\myagent\.hermes\plugins\write-guard")

# 需要部署的核心文件（测试文件不进部署目录）
FILES = ["__init__.py", "handler.py", "plugin.yaml"]


def main() -> int:
    print("==> [1/4] 检查源目录")
    if not SRC.is_dir():
        print(f"错误: 源目录不存在 {SRC}")
        return 1

    print("==> [2/4] 创建部署目录")
    DST.mkdir(parents=True, exist_ok=True)

    print("==> [3/4] 同步文件并清理旧缓存")
    for f in FILES:
        src_file = SRC / f
        if not src_file.is_file():
            print(f"错误: 缺少源文件 {src_file}")
            return 1
        shutil.copy2(src_file, DST / f)
        print(f"  已同步 {f}")
    # 清理部署目录的 Python 字节码缓存，避免 Gateway 加载旧 .pyc
    pycache = DST / "__pycache__"
    if pycache.is_dir():
        shutil.rmtree(pycache)
        print(f"  已清理 {pycache}")

    print("==> [4/4] 校验")
    # 语法检查（在部署目录下用相对文件名，避免 Windows 路径转义问题）
    subprocess.run(
        [sys.executable, "-m", "py_compile", "__init__.py", "handler.py"],
        cwd=str(DST),
        check=True,
    )
    print("  语法检查通过")

    # 一致性对比：源 vs 部署
    ok = True
    for f in FILES:
        if (SRC / f).read_bytes() == (DST / f).read_bytes():
            print(f"  OK   {f} 一致")
        else:
            print(f"  FAIL {f} 不一致")
            ok = False
    if not ok:
        return 1

    print()
    print(f"部署完成: {SRC} -> {DST}")
    print("注意: 插件改动需重启 Gateway 才生效（当前会话不热加载）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
