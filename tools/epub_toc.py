#!/usr/bin/env python3
"""从 EPUB 的 NCX / nav.xhtml 取真目录，生成 chapters.json（章节名 + 起止字符位置）。

不修改 source/original.txt。偏移以传入的 txt 为准：
    先按 import_local 的同一套逻辑重构文本，若与 txt 完全一致，偏移就是精确的；
    若不一致，退化为在 txt 里按标题顺序查找，并在结果里标记 aligned=false。

用法:
    python tools/epub_toc.py --epub "某书.epub" --txt "Books/46_某书/source/original.txt" \
        --out "Books/46_某书/source/chapters.json"
"""

import argparse
import hashlib
import json
import unicodedata
import posixpath
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from bs4 import BeautifulSoup

try:
    import opencc
except Exception:  # noqa: BLE001
    opencc = None


def local(tag: str) -> str:
    return tag.split("}")[-1]


def parse_opf(z: zipfile.ZipFile) -> tuple[str, list[str], dict[str, str]]:
    container = z.read("META-INF/container.xml").decode("utf-8", "replace")
    opf_path = re.search(r'full-path="([^"]+)"', container).group(1)
    opf = z.read(opf_path).decode("utf-8", "replace")
    manifest: dict[str, str] = {}
    for item in re.findall(r"<item\b[^>]*>", opf, re.I):
        i = re.search(r'\bid="([^"]+)"', item)
        h = re.search(r'\bhref="([^"]+)"', item)
        if i and h:
            manifest[i.group(1)] = h.group(1)
    spine = [
        manifest[x]
        for x in re.findall(r'<itemref\b[^>]*\bidref="([^"]+)"', opf, re.I)
        if x in manifest
    ]
    return opf_path, spine, manifest


def parse_ncx(z: zipfile.ZipFile, names: list[str]) -> list[tuple[int, str, str]]:
    ncx = next((n for n in names if n.lower().endswith(".ncx")), None)
    if not ncx:
        return []
    root = ET.fromstring(z.read(ncx))
    navmap = next((c for c in root if local(c.tag) == "navMap"), None)
    if navmap is None:
        return []
    out: list[tuple[int, str, str]] = []

    def walk(node, depth):
        for child in node:
            if local(child.tag) != "navPoint":
                continue
            title, src = "", ""
            for c in child:
                if local(c.tag) == "navLabel":
                    for x in c:
                        if local(x.tag) == "text":
                            title = (x.text or "").strip()
                elif local(c.tag) == "content":
                    src = c.attrib.get("src", "")
            if title and src:
                out.append((depth, title, src))
            walk(child, depth + 1)

    walk(navmap, 0)
    return out


def parse_nav(z: zipfile.ZipFile, names: list[str]) -> list[tuple[int, str, str]]:
    nav = next((n for n in names if n.lower().endswith(("nav.xhtml", "toc.xhtml"))), None)
    if not nav:
        return []
    soup = BeautifulSoup(z.read(nav).decode("utf-8", "replace"), "html.parser")
    toc = soup.find(attrs={"epub:type": "toc"}) or soup.find("nav") or soup
    out: list[tuple[int, str, str]] = []

    def walk_list(ol, depth):
        for li in ol.find_all("li", recursive=False):
            a = li.find("a", recursive=False)
            if a and a.get("href"):
                out.append((depth, a.get_text(" ", strip=True), a["href"]))
            sub = li.find("ol", recursive=False)
            if sub:
                walk_list(sub, depth + 1)

    for ol in toc.find_all("ol"):
        if not ol.find_parent("li"):
            walk_list(ol, 0)
    return out


def norm_text(text: str) -> str:
    """与 Book_Agent_Pipeline/tools/prepare.py 的 normalize 保持一致。"""
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def doc_key(href: str) -> str:
    return href.split("#", 1)[0]


def extract(z: zipfile.ZipFile, spine: list[str], opf_path: str, conv=None) -> tuple[str, list[tuple[int, int, str]]]:
    """按 import_local 的逻辑重构全文，记录每个 spine 文档的 (start, end, href)。"""
    base = posixpath.dirname(opf_path)
    parts, docs, offset = [], [], 0
    for href in spine:
        full = posixpath.normpath(posixpath.join(base, href))
        try:
            soup = BeautifulSoup(z.read(full).decode("utf-8", "replace"), "html.parser")
        except KeyError:
            continue
        for tag in soup(["script", "style"]):
            tag.decompose()
        lines = [l.strip() for l in soup.get_text("\n").split("\n") if l.strip()]
        if not lines:
            continue
        text = "\n\n".join(lines)
        if conv:
            text = conv(text)
        text = norm_text(text)
        if parts:
            offset += 2  # 文档之间的 \n\n
        start = offset
        parts.append(text)
        offset += len(text)
        docs.append((start, offset, href))
    return "\n\n".join(parts), docs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--epub", required=True)
    ap.add_argument("--txt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-level", type=int, default=1, help="目录树里保留到第几层（0=只保留章）")
    ap.add_argument("--simplified", action="store_true", help="先把 EPUB 文本繁转简再对齐（用于简体化过的 TXT）")
    args = ap.parse_args()

    epub = Path(args.epub)
    txt = Path(args.txt).read_text(encoding="utf-8")
    target = txt.strip()

    conv = None
    if args.simplified:
        if opencc is None:
            raise SystemExit("需要 opencc-python-reimplemented")
        conv = opencc.OpenCC("t2s").convert

    with zipfile.ZipFile(epub) as z:
        names = z.namelist()
        opf_path, spine, _ = parse_opf(z)
        toc = parse_ncx(z, names) or parse_nav(z, names)
        if conv:
            toc = [(d, conv(t), h) for d, t, h in toc]
        rebuilt, docs = extract(z, spine, opf_path, conv)

    aligned = rebuilt.strip() == target
    # 文档起点 → 章标题：取指向该文档的最浅目录项
    title_of: dict[str, tuple[int, str]] = {}
    for depth, title, src in toc:
        key = doc_key(src)
        if key not in title_of or depth < title_of[key][0]:
            title_of[key] = (depth, title)

    chapters = []
    for start, end, href in docs:
        title = title_of.get(href)
        if not title:
            continue
        chapters.append({"title": title[1], "level": title[0], "start": start, "end": end, "href": href})

    # 文档之间补空档，保证 start/end 连续覆盖
    chapters.sort(key=lambda c: c["start"])
    for i, c in enumerate(chapters):
        c["end"] = chapters[i + 1]["start"] if i + 1 < len(chapters) else len(target)

    tree = [
        {"title": t, "level": d, "href": s}
        for d, t, s in toc
        if d <= args.max_level
    ]
    data = {
        "source_epub": epub.name,
        "source_txt": str(txt),
        "aligned": aligned,
        "rebuilt_matches_txt": aligned,
        "total_chars": len(target),
        "txt_sha256": hashlib.sha256(target.encode("utf-8")).hexdigest(),
        "chapter_count": len(chapters),
        "chapters": chapters,
        "toc": tree,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")

    print(f"EPUB 目录项: {len(toc)}；对齐文档章节: {len(chapters)}；txt 字数: {len(target)}")
    print(f"重构文本与 txt 一致: {aligned}")
    for c in chapters[:15]:
        print(f"  [{c['start']:>7} - {c['end']:>7}] {c['title'][:40]}")
    if len(chapters) > 15:
        print(f"  ... 共 {len(chapters)} 章")
    print(f"已写入 {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
