#!/usr/bin/env python3
"""write-guard 一键部署脚本（Windows / 跨平台）

用法: python deploy.py [源目录] [部署目录]
      缺省：源 = D:\\myagent\\workspace\\write-guard
            部署 = D:\\myagent\\.hermes\\plugins\\write-guard
作用: 将 workspace 源目录的核心文件同步到 Hermes 插件部署目录，
      清理旧字节码缓存，校验语法与传输完整性。
不拷贝测试文件（部署目录仅需 __init__.py / handler.py / plugin.yaml，
plugin.yaml 只注册 handler 的 hook；测试文件留在 workspace 运行）。
"""

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_SRC = Path(r"D:\myagent\workspace\write-guard")
DEFAULT_DST = Path(r"D:\myagent\.hermes\plugins\write-guard")

# 需要部署的核心文件（测试文件不进部署目录）
FILES = ["__init__.py", "handler.py", "plugin.yaml"]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def main(argv) -> int:
    src = Path(argv[1]) if len(argv) > 1 else DEFAULT_SRC
    dst = Path(argv[2]) if len(argv) > 2 else DEFAULT_DST

    print("==> [1/4] 检查源目录")
    if not src.is_dir():
        print(f"错误: 源目录不存在 {src}")
        return 1

    print("==> [2/4] 创建部署目录")
    dst.mkdir(parents=True, exist_ok=True)

    print("==> [3/4] 同步文件并清理旧缓存")
    src_hashes = {}
    for f in FILES:
        src_file = src / f
        if not src_file.is_file():
            print(f"错误: 缺少源文件 {src_file}")
            return 1
        src_hashes[f] = _sha(src_file)        # 复制前先锚定源哈希
        shutil.copy2(src_file, dst / f)
        print(f"  已同步 {f}")
    # 清理部署目录的 Python 字节码缓存，避免 Gateway 加载旧 .pyc
    pycache = dst / "__pycache__"
    if pycache.is_dir():
        shutil.rmtree(pycache)
        print(f"  已清理 {pycache}")

    print("==> [4/4] 校验")
    # 语法检查（在部署目录下用相对文件名，避免 Windows 路径转义问题）。
    # 失败时给出可读报错并返回码，不外抛裸 traceback。
    proc = subprocess.run(
        [sys.executable, "-m", "py_compile", "__init__.py", "handler.py"],
        cwd=str(dst),
    )
    if proc.returncode != 0:
        print("  FAIL 部署文件语法检查未通过（见上方 py_compile 输出）")
        return 1
    print("  语法检查通过")

    # 传输完整性：部署文件哈希 == 复制前锚定的源哈希。
    # 比对基准是「复制前快照」而非复制后重读源，因此校验的是磁盘传输本身，
    # 不是自我确认（修复旧版 copy2 后读两边必然相等的自指问题）。
    ok = True
    for f in FILES:
        dst_hash = _sha(dst / f)
        if dst_hash == src_hashes[f]:
            print(f"  OK   {f} 传输一致 (sha256:{dst_hash})")
        else:
            print(f"  FAIL {f} 部署后内容与源不一致 "
                  f"(源 {src_hashes[f]} != 部署 {dst_hash})")
            ok = False
    if not ok:
        return 1

    print()
    print(f"部署完成: {src} -> {dst}")
    print("注意: 插件改动需重启 Gateway 才生效（当前会话不热加载）")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
