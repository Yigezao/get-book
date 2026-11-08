#!/usr/bin/env python3
"""把「待导入/」里的 txt / epub 转成标准书籍目录。

用法:
    python tools/import_local.py
    python tools/import_local.py --file "待导入/某本书.epub" --title 书名 --author 作者

流程:
    读取 txt / epub → 提取正文 → 写入 Books/<书名>/source/original.txt + meta.json
    → 原文件移到 待导入/已处理/ → 运行 build_catalog.py（加序号、刷新总目录、同步 TXT全文）

文件名建议:
    书名.txt / 书名-作者.txt / 书名_作者.txt
    EPUB 优先读内嵌的 dc:title / dc:creator。
"""

import argparse
import json
import posixpath
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_gutenberg import CJK_RE, unwrap  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "Books"
INBOX = ROOT / "待导入"
DONE = INBOX / "已处理"
KANA_RE = re.compile(r"[ぁ-んァ-ヶー]")
SKIP = {"readme.txt", "说明.txt"}


def decode(raw: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", "gb18030", "big5"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def norm(s: str) -> str:
    return re.sub(r"[\s　\W_]+", "", s).casefold()


def detect_lang(text: str) -> str:
    cjk = len(CJK_RE.findall(text))
    kana = len(KANA_RE.findall(text))
    latin = len(re.findall(r"[A-Za-z]", text))
    if kana > 50:
        return "ja"
    if cjk > latin * 0.3:
        return "zh"
    return "en"


def txt_body(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\xa0", " ").lstrip("﻿")
    lines = text.split("\n")
    nonempty = [l.strip() for l in lines if l.strip()]
    blanks = sum(1 for l in lines if not l.strip())
    indented = sum(1 for l in nonempty if l[:1] in (" ", "\t", "　"))
    if blanks >= 3 or indented >= max(3, len(nonempty) // 20):
        return unwrap("\n".join(lines))
    return "\n\n".join(nonempty)


def meta_text(raw: str) -> str:
    return BeautifulSoup(raw, "html.parser").get_text(" ", strip=True)


def epub_parse(path: Path) -> tuple[str, str, str, str]:
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        container = z.read("META-INF/container.xml").decode("utf-8", "replace")
        m = re.search(r'full-path="([^"]+)"', container)
        if not m:
            raise ValueError("EPUB 缺少 container.xml")
        opf_path = unquote(m.group(1))
        opf = z.read(opf_path).decode("utf-8", "replace")

        def dc(tag: str) -> str:
            hit = re.search(rf"<dc:{tag}\b[^>]*>(.*?)</dc:{tag}>", opf, re.S | re.I)
            return meta_text(hit.group(1)) if hit else ""

        title, author, lang = dc("title"), dc("creator"), dc("language")

        manifest = {}
        for item in re.findall(r"<item\b[^>]*>", opf, re.I):
            id_ = re.search(r'\bid="([^"]+)"', item)
            href = re.search(r'\bhref="([^"]+)"', item)
            if id_ and href:
                manifest[id_.group(1)] = unquote(href.group(1))
        spine = re.findall(r'<itemref\b[^>]*\bidref="([^"]+)"', opf, re.I)

        parts = []
        base = posixpath.dirname(opf_path)
        for idref in spine:
            href = manifest.get(idref)
            if not href:
                continue
            full = posixpath.normpath(posixpath.join(base, href))
            if full not in names:
                continue
            soup = BeautifulSoup(z.read(full).decode("utf-8", "replace"), "html.parser")
            for tag in soup(["script", "style"]):
                tag.decompose()
            lines = [l.strip() for l in soup.get_text("\n").split("\n") if l.strip()]
            if lines:
                parts.append("\n\n".join(lines))
        return "\n\n".join(parts), title, author, lang


def split_filename(stem: str) -> tuple[str, str]:
    for sep in ("—", "_", "-"):
        if sep not in stem:
            continue
        if sep == "-" and not CJK_RE.search(stem):
            continue
        a, b = stem.rsplit(sep, 1)
        if 1 <= len(b.strip()) <= 12 and CJK_RE.search(b + a):
            return a.strip(), b.strip()
    return stem.strip(), ""


def existing_titles() -> set[str]:
    titles = set()
    for d in BOOKS.iterdir():
        if not d.is_dir():
            continue
        p = d / "meta.json"
        if p.exists():
            try:
                titles.add(norm(json.loads(p.read_text(encoding="utf-8")).get("title", "")))
            except Exception:
                pass
        titles.add(norm(re.sub(r"^\d+_", "", d.name)))
    return titles


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="只处理一个文件")
    ap.add_argument("--title", default="")
    ap.add_argument("--author", default="")
    ap.add_argument("--lang", default="")
    ap.add_argument("--inbox", default=str(INBOX))
    ap.add_argument("--no-catalog", action="store_true")
    ap.add_argument("--keep", action="store_true", help="处理完不移动原文件")
    args = ap.parse_args()

    inbox = Path(args.inbox)
    done = inbox / "已处理"
    done.mkdir(parents=True, exist_ok=True)

    files = [Path(args.file)] if args.file else sorted(
        p for p in inbox.iterdir()
        if p.is_file() and p.suffix.lower() in (".txt", ".epub") and p.name.lower() not in SKIP
    )
    if not files:
        print(f"待导入目录是空的: {inbox}")
        return 0

    known = existing_titles()
    ok, skipped, failed = [], [], []
    for path in files:
        try:
            if path.suffix.lower() == ".epub":
                body, m_title, m_author, m_lang = epub_parse(path)
            else:
                body, m_title, m_author, m_lang = decode(path.read_bytes()), "", "", ""
        except Exception as e:  # noqa: BLE001
            print(f"[FAIL] {path.name}: 读取失败 {e}")
            failed.append(path.name)
            continue

        body = re.sub(r"\n{3,}", "\n\n", body).strip()
        title = args.title or m_title or split_filename(path.stem)[0]
        author = args.author or m_author or split_filename(path.stem)[1]
        lang = args.lang or m_lang or detect_lang(body)
        lang = lang.lower().replace("_", "-")
        lang = "zh" if lang.startswith("zh") else ("ja" if lang.startswith("ja") else lang)

        cjk = len(CJK_RE.findall(body))
        jp = cjk + len(KANA_RE.findall(body))
        words = len(body.split())
        enough = (jp >= 300) if lang in ("zh", "ja") else (words >= 100)
        if not enough:
            print(f"[FAIL] {path.name}: 正文太短（{jp} 字 / {words} 词）")
            failed.append(path.name)
            continue
        if norm(title) in known:
            print(f"[SKIP] {path.name}: 《{title}》已存在")
            skipped.append(path.name)
            continue

        dest = BOOKS / title
        if dest.exists():
            print(f"[SKIP] {path.name}: 目录已存在 {dest.name}")
            skipped.append(path.name)
            continue
        (dest / "source").mkdir(parents=True, exist_ok=True)
        (dest / "source" / "original.txt").write_text(body + "\n", encoding="utf-8", newline="\n")
        meta = {
            "title": title,
            "author": author,
            "language": lang,
            "script": "simplified" if lang == "zh" else ("japanese" if lang == "ja" else "latin"),
            "source_type": "local_import",
            "source": path.name,
            "imported_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
            "stats": {
                "chars": len(body),
                "paragraphs": len([p for p in body.split("\n\n") if p.strip()]),
                "cjk_chars": cjk if lang == "zh" else None,
                "japanese_chars": jp if lang == "ja" else None,
                "words": words if lang not in ("zh", "ja") else None,
            },
            "verification": {"min_length": True, "has_paragraphs": True},
        }
        (dest / "meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
        )
        known.add(norm(title))
        ok.append(title)
        print(f"[OK] {path.name} -> 《{title}》 {jp or words} {'字' if lang in ('zh','ja') else '词'}")

        if not args.keep:
            target = done / path.name
            if target.exists():
                target = done / f"{path.stem}_{datetime.now():%Y%m%d%H%M%S}{path.suffix}"
            shutil.move(str(path), str(target))

    print(f"\n完成：新增 {len(ok)}，跳过 {len(skipped)}，失败 {len(failed)}")
    if ok and not args.no_catalog:
        r = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools" / "build_catalog.py")])
        if r.returncode != 0:
            print("[WARN] 目录重建失败，请检查 build_catalog.py")
    return 0 if not failed else 2


if __name__ == "__main__":
    sys.exit(main())
