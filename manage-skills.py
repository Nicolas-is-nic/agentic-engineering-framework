#!/usr/bin/env python3
"""
Agentic Engineering Framework 技能包安装/卸载脚本

用法:
    python3 manage-skills.py install      # 安装
    python3 manage-skills.py uninstall    # 卸载
    python3 manage-skills.py status       # 查看安装状态

安装时会在目标目录生成 .agentic-framework-manifest 记录清单，
卸载时按清单精准删除，不影响用户已有文件。
"""

import sys
import os
import shutil
from datetime import datetime
from pathlib import Path

# ============================================================
# 配置区域（按需修改）
# ============================================================

# 源目录：框架项目根目录（脚本通过自身位置自动推导，一般无需修改）
SOURCE_DIR = Path(__file__).resolve().parent

# 目标目录：Agent 配置目录
DEST_DIR = Path.home() / ".claude"

# ============================================================

MANIFEST_NAME = ".agentic-framework-manifest"
DIRS_TO_INSTALL = ["agents", "skills", "commands"]


def info(msg: str) -> None:
    print(f"\033[0;34m[INFO]\033[0m {msg}")


def ok(msg: str) -> None:
    print(f"\033[0;32m[OK]\033[0m {msg}")


def warn(msg: str) -> None:
    print(f"\033[0;33m[WARN]\033[0m {msg}")


def fatal(msg: str) -> None:
    print(f"\033[0;31m[ERROR]\033[0m {msg}")
    sys.exit(1)


def manifest_path() -> Path:
    return DEST_DIR / MANIFEST_NAME


def load_manifest() -> list[str]:
    """读取清单文件，返回已安装文件的相对路径列表。"""
    mp = manifest_path()
    if not mp.is_file():
        return []
    lines = mp.read_text(encoding="utf-8").splitlines()
    return [line for line in lines if line and not line.startswith("#")]


def save_manifest(entries: list[str]) -> None:
    """保存清单文件（原子写入：先写临时文件再 rename）。"""
    mp = manifest_path()
    mp.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "# Agentic Engineering Framework 安装清单",
        f"# 由 manage-skills.py 于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 生成",
        "# 请勿手动修改此文件",
        "",
    ]
    tmp = mp.with_suffix(".tmp")
    tmp.write_text("\n".join(header + entries) + "\n", encoding="utf-8")
    tmp.replace(mp)


# ============================================================
# 安装
# ============================================================

def do_install() -> None:
    # 校验源目录
    for d in DIRS_TO_INSTALL:
        if not (SOURCE_DIR / d).is_dir():
            fatal(f"源目录中缺少 {d}/")

    # 已安装则先卸载
    if manifest_path().is_file():
        warn("检测到已有安装清单，将先执行卸载再重新安装。")
        do_uninstall()

    DEST_DIR.mkdir(parents=True, exist_ok=True)

    entries: list[str] = []
    count = 0

    info(f"安装技能包: {SOURCE_DIR} -> {DEST_DIR}")

    for d in DIRS_TO_INSTALL:
        src_root = SOURCE_DIR / d
        if not src_root.is_dir():
            continue
        for src_file in sorted(src_root.rglob("*")):
            if not src_file.is_file():
                continue
            # 跳过符号链接文件（不跟踪）
            if src_file.is_symlink():
                continue

            relpath = src_file.relative_to(SOURCE_DIR)
            dst_file = DEST_DIR / relpath

            # 复制文件（已存在则覆盖）
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src_file), str(dst_file))
            entries.append(str(relpath))
            count += 1

    save_manifest(entries)
    ok(f"安装完成，共安装 {count} 个文件。")


# ============================================================
# 卸载
# ============================================================

def do_uninstall() -> None:
    mp = manifest_path()
    if not mp.is_file():
        fatal(f"未找到安装清单: {mp}（可能未安装过）")

    entries = load_manifest()
    count = 0
    failed: list[str] = []

    for relpath in entries:
        target = DEST_DIR / relpath
        try:
            if target.is_file() and not target.is_symlink():
                target.unlink()
                count += 1
            else:
                warn(f"文件不存在或非普通文件，跳过: {relpath}")
        except OSError as e:
            failed.append(relpath)
            warn(f"无法删除 {relpath}: {e}")

    # 清理空目录（从深到浅，只删空目录）
    for d in DIRS_TO_INSTALL:
        root = DEST_DIR / d
        if not root.is_dir():
            continue
        for dirpath in sorted(
            (p for p in root.rglob("*") if p.is_dir()),
            key=lambda p: len(p.parts),
            reverse=True,
        ):
            try:
                if dirpath.is_dir() and not any(dirpath.iterdir()):
                    dirpath.rmdir()
            except OSError:
                pass

    # 删除清单
    try:
        mp.unlink()
    except OSError:
        pass

    ok(f"卸载完成，共删除 {count} 个文件。")
    if failed:
        warn(f"以下 {len(failed)} 个文件删除失败，需手动处理:")
        for f in failed:
            print(f"  {f}")


# ============================================================
# 状态查看
# ============================================================

def do_status() -> None:
    mp = manifest_path()
    if mp.is_file():
        entries = load_manifest()
        ok(f"已安装到 {DEST_DIR}（{len(entries)} 个文件）")
        print()
        info("已安装的文件:")
        for e in entries:
            print(f"  {e}")
    else:
        warn(f"未安装到 {DEST_DIR}")


# ============================================================
# 主入口
# ============================================================

def main() -> None:
    if len(sys.argv) < 2:
        print(f"用法: {sys.argv[0]} <install|uninstall|status>")
        sys.exit(1)

    action = sys.argv[1]
    if action == "install":
        do_install()
    elif action == "uninstall":
        do_uninstall()
    elif action == "status":
        do_status()
    else:
        fatal(f"未知命令: {action}")


if __name__ == "__main__":
    main()
