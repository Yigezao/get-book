#!/usr/bin/env python3
"""给所有源自 EPUB 的书批量生成 source/chapters.json。

只处理 meta.source 以 .epub 结尾、且 EPUB 原件还在 待导入/已处理/ 的书。
epub_toc.py 报告 aligned=false 时删除结果，避免写入错误偏移。
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "Books"
DONE = ROOT / "待导入" / "已处理"
TOC = ROOT / "tools" / "epub_toc.py"


def find_epub(name: str) -> Path | None:
    exact = DONE / name
    if exact.exists():
        return exact
    matches = list(DONE.glob(name.split(" (")[0] + "*.epub"))
    return matches[0] if matches else None


def main() -> int:
    ok, skipped, failed = [], [], []
    for book in sorted(BOOKS.iterdir()):
        meta_path = book / "meta.json"
        if not book.is_dir() or not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        src = str(meta.get("source", ""))
        if not src.lower().endswith(".epub"):
            continue
        epub = find_epub(src)
        if not epub:
            skipped.append((book.name, "EPUB 原件不在 已处理/"))
            continue
        txt = book / "source" / "original.txt"
        out = book / "source" / "chapters.json"
        r = subprocess.run(
            [sys.executable, "-X", "utf8", str(TOC), "--epub", str(epub), "--txt", str(txt), "--out", str(out)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if r.returncode != 0:
            failed.append((book.name, "脚本失败"))
            continue
        data = json.loads(out.read_text(encoding="utf-8"))
        if not data.get("aligned"):
            # 繁转简过的书：再按简体对齐一次
            subprocess.run(
                [sys.executable, "-X", "utf8", str(TOC), "--epub", str(epub), "--txt", str(txt),
                 "--out", str(out), "--simplified"],
                capture_output=True, text=True, encoding="utf-8",
            )
            data = json.loads(out.read_text(encoding="utf-8"))
            if not data.get("aligned"):
                out.unlink(missing_ok=True)
                failed.append((book.name, "文本已改动，偏移对不上"))
                continue
        ok.append((book.name, data["chapter_count"], data["total_chars"]))

    print(f"成功 {len(ok)} 本")
    for name, n, total in ok:
        print(f"  {name}: {n} 章 / {total:,} 字")
    if skipped:
        print(f"跳过 {len(skipped)} 本")
        for name, why in skipped:
            print(f"  {name}: {why}")
    if failed:
        print(f"失败 {len(failed)} 本")
        for name, why in failed:
            print(f"  {name}: {why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
