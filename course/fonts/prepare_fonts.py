"""Noto Sans JP (Regular / Bold) の TTF を生成するスクリプト。

Google Fonts の Noto Sans JP は npm パッケージ @fontsource/noto-sans-jp で
サブセット化された woff2 として配布されている。本スクリプトはそれを取得し、
全サブセットを結合して 1 本の TTF（Regular / Bold）に戻す。

生成物: course/fonts/NotoSansJP-Regular.ttf, NotoSansJP-Bold.ttf
（ライセンス: SIL Open Font License 1.1）

使い方:
    pip install fonttools brotli
    python course/fonts/prepare_fonts.py
"""

import glob
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PACKAGE = "@fontsource/noto-sans-jp"


def fetch_package(workdir: str) -> str:
    """npm pack でパッケージを取得して展開し、files ディレクトリのパスを返す。"""
    subprocess.run(["npm", "pack", PACKAGE], cwd=workdir, check=True,
                   stdout=subprocess.DEVNULL)
    tgz = glob.glob(os.path.join(workdir, "*.tgz"))[0]
    subprocess.run(["tar", "xzf", tgz], cwd=workdir, check=True)
    return os.path.join(workdir, "package", "files")


def build(files_dir: str, weight: str, out_name: str, workdir: str) -> None:
    from fontTools.merge import Merger
    from fontTools.ttLib import TTFont

    sources = sorted(glob.glob(os.path.join(files_dir, f"noto-sans-jp-*-{weight}-normal.woff2")))
    if not sources:
        raise SystemExit(f"サブセットが見つかりません: {files_dir}")

    ttfs = []
    for i, path in enumerate(sources):
        font = TTFont(path)
        font.flavor = None  # woff2 -> ttf
        tmp = os.path.join(workdir, f"tmp_{weight}_{i}.ttf")
        font.save(tmp)
        ttfs.append(tmp)

    merged = Merger().merge(ttfs)
    for name_id in (1, 4, 6):
        merged["name"].setName(out_name, name_id, 3, 1, 0x409)
    dest = os.path.join(HERE, f"{out_name}.ttf")
    merged.save(dest)
    print(f"生成: {dest}  ({len(merged.getBestCmap())} glyphs)")


def main() -> None:
    workdir = tempfile.mkdtemp(prefix="notojp-")
    try:
        files_dir = fetch_package(workdir)
        build(files_dir, "400", "NotoSansJP-Regular", workdir)
        build(files_dir, "700", "NotoSansJP-Bold", workdir)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
