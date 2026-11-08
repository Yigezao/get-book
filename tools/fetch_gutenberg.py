#!/usr/bin/env python3
"""从 Project Gutenberg / Gutendex 抓取公版书全文（支持中英文），清洗后输出标准目录。

用法:
    # 英文
    python tools/fetch_gutenberg.py --query "gift of the magi" --title 麦琪的礼物 --author 欧·亨利
    # 中文（书名建议用繁体查，简繁会自动兜底）
    python tools/fetch_gutenberg.py --query 朝花夕拾 --lang zh --title 朝花夕拾 --author 鲁迅

输出:
    Books/<title>/source/original.txt   清洗后的正文（段落已合行；中文默认转简体）
    Books/<title>/source/raw.txt        原始下载文件
    Books/<title>/meta.json             来源、字数、校验结果

校验不通过时退出码为 2，并且不写 original.txt —— 宁可不产出，也不产出半本书。
"""

import argparse
import hashlib
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

API = "https://gutendex.com/books"
UA = "BookGetter/1.0 (personal use; public domain texts)"
TIMEOUT = 60
RETRIES = 3
CJK_RE = re.compile(r"[㐀-䶿一-鿿豈-﫿]")

try:  # 可选依赖：繁转简
    import opencc

    _T2S = opencc.OpenCC("t2s")
    _S2T = opencc.OpenCC("s2t")
except Exception:  # noqa: BLE001 - 没装就保留原文
    _T2S = _S2T = None


def http_get(url: str) -> bytes:
    last = None
    for i in range(RETRIES):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001 - 网络错误全部重试
            last = e
            if i < RETRIES - 1:
                time.sleep(2 * (i + 1))
    raise RuntimeError(f"下载失败 {url}: {last}")


def normalize(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"\W+", "", s).casefold()


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def search(query: str, lang: str | None) -> list[dict]:
    params = {"search": query}
    if lang:
        params["languages"] = lang
    url = f"{API}?{urllib.parse.urlencode(params)}"
    return json.loads(http_get(url).decode("utf-8")).get("results", [])


def get_book(book_id: int) -> dict:
    return json.loads(http_get(f"{API}/{book_id}").decode("utf-8"))


def pick_text_url(book: dict) -> str | None:
    """优先 UTF-8 纯文本，其次 us-ascii 纯文本；跳过 zip 和 readme。"""
    cands = []
    for mime, url in book.get("formats", {}).items():
        if not mime.startswith("text/plain"):
            continue
        low = url.lower()
        if low.endswith(".zip") or "readme" in low:
            continue
        score = 0
        if "utf-8" in mime.lower():
            score -= 10
        if "/ebooks/" in low:  # 新式稳定地址优先
            score -= 5
        cands.append((score, url))
    return sorted(cands)[0][1] if cands else None


def find_book(query: str, lang: str | None) -> dict | None:
    results = search(query, lang)
    if not results:
        # 简体查不到时，用繁体再试一次（Gutenberg 中文目录多为繁体正题名）
        alt = _S2T.convert(query) if _S2T else None
        if alt and alt != query:
            results = search(alt, lang)
    results = [b for b in results if pick_text_url(b)]
    if not results:
        return None
    results.sort(key=lambda b: (-similarity(query, b["title"]), -b.get("download_count", 0)))
    return results[0]


def decode(raw: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def strip_boilerplate(text: str) -> tuple[str, bool]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    sm = re.search(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", text, re.S | re.I)
    em = re.search(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", text, re.S | re.I)
    if not (sm and em) or em.start() <= sm.end():
        body, ok = text.strip("\n"), False
    else:
        body, ok = text[sm.end():em.start()].strip("\n"), True
    return strip_trailing_credits(strip_credits(body)), ok


def strip_trailing_credits(text: str) -> str:
    """去掉 END 标记前那几行 "End of Project Gutenberg's ..." 及出版方制作行。"""
    lines = text.split("\n")
    pat = re.compile(
        r"^(end of (the )?project gutenberg|produced by|credits?:|updated editions will"
        r"|the full project gutenberg|start: full license)",
        re.I,
    )
    j = len(lines)
    while j > 0:
        s = lines[j - 1].strip()
        if (
            not s
            or pat.match(s)
            or "香港子才" in s
            or re.match(r"^\*?制作[：:]", s)
        ):
            j -= 1
        else:
            break
    return "\n".join(lines[:j])


def strip_credits(text: str) -> str:
    """去掉 START 标记后紧跟的致谢行（Produced by / Credits 等）。"""
    lines = text.split("\n")
    i = 0
    while i < len(lines) and i < 10 and not lines[i].strip():
        i += 1
    j = i
    pat = re.compile(r"^(produced by|credits?:|e-text prepared|transcribed|proofread|updated editions)", re.I)
    while j < len(lines) and (not lines[j].strip() or pat.match(lines[j].strip())):
        j += 1
    return "\n".join(lines[j:]) if j > i else text


def looks_like_heading(line: str) -> bool:
    """短、无句末标点 —— 中文排版里的篇名/小节名。"""
    return len(line) <= 12 and not re.search(r"[。！？!?；;：:，,、]$", line)


def unwrap(text: str) -> str:
    """合行成段。

    中文古籍/民国排版的段落靠行首缩进（全角空格或 4 个半角空格）标记，段内硬换行；
    英文 Gutenberg 靠空行分段。两种都按「空行 或 缩进」断段，段内中文不加空格。
    """
    cjk_ratio = len(CJK_RE.findall(text)) / max(1, len(re.sub(r"\s", "", text)))
    joiner = "" if cjk_ratio > 0.2 else " "

    paras, buf = [], []
    last_indented = False
    for line in text.split("\n"):
        if not line.strip():
            if buf:
                paras.append(joiner.join(buf))
                buf = []
                last_indented = False
            continue
        indented = line[:1] in (" ", "\t", "　")
        stripped = line.strip()
        # 民国版式常见「右对齐日期行 + 下一行篇名」，两行间没有空行，单独拆开
        signature_then_title = (
            buf
            and last_indented
            and not indented
            and looks_like_heading(stripped)
            and len(buf[-1]) <= 25
            and buf[-1].endswith("。")
        )
        if (indented or signature_then_title) and buf:
            paras.append(joiner.join(buf))
            buf = [stripped]
        else:
            buf.append(stripped)
        last_indented = indented
    if buf:
        paras.append(joiner.join(buf))
    return "\n\n".join(paras)


def convert_simplified(text: str) -> tuple[str, bool]:
    if not _T2S:
        return text, False
    converted = _T2S.convert(text)
    return converted, converted != text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", help="书名/作者，用于 Gutendex 搜索")
    ap.add_argument("--id", type=int, help="直接指定 Gutenberg 书号")
    ap.add_argument("--lang", default=None, help="语言过滤：en / zh / fr ...")
    ap.add_argument("--title", required=True, help="输出用的书名（中文名）")
    ap.add_argument("--author", default="", help="作者")
    ap.add_argument("--out", default=None, help="输出根目录，默认 Books/")
    ap.add_argument("--min-words", type=int, default=150, help="英文低于此词数视为失败")
    ap.add_argument("--min-chars", type=int, default=300, help="中文低于此字数（汉字）视为失败")
    ap.add_argument("--no-unwrap", action="store_true", help="保留原始硬换行")
    ap.add_argument("--keep-traditional", action="store_true", help="不转简体")
    args = ap.parse_args()

    if not args.id and not args.query:
        ap.error("需要 --query 或 --id")

    out_root = Path(args.out) if args.out else Path(__file__).resolve().parent.parent / "Books"
    dest = out_root / args.title
    src = dest / "source"

    # 1. 选书
    if args.id:
        book = get_book(args.id)
    else:
        book = find_book(args.query, args.lang)
        if not book:
            print(f"[FAIL] Gutendex 无结果: {args.query} (lang={args.lang})", file=sys.stderr)
            return 2

    url = pick_text_url(book)
    if not url:
        print(f"[FAIL] 该书无可用纯文本: {book.get('title')}", file=sys.stderr)
        return 2

    lang = (book.get("languages") or ["en"])[0]
    print(f"选中: #{book['id']} {book['title']} | {', '.join(a['name'] for a in book.get('authors', []))} | {lang}")
    print(f"来源: {url}")

    # 2. 下载 + 清洗
    raw = http_get(url)
    raw_text = decode(raw)
    body, markers_ok = strip_boilerplate(raw_text)
    text = body if args.no_unwrap else unwrap(body)

    is_cjk = len(CJK_RE.findall(text)) / max(1, len(re.sub(r"\s", "", text))) > 0.2
    converted = False
    if is_cjk and not args.keep_traditional:
        text, converted = convert_simplified(text)

    # 3. 校验（失败就不落盘 original.txt）
    cjk_chars = len(CJK_RE.findall(text))
    words = len(text.split())
    paragraphs = len([p for p in text.split("\n\n") if p.strip()])
    bad_chars = text.count("�")
    boiler = len(re.findall(r"Project Gutenberg|gutenberg\.org", text, re.I))
    checks = {
        "markers_found": markers_ok,
        "min_length": (cjk_chars >= args.min_chars) if is_cjk else (words >= args.min_words),
        "no_replacement_chars": bad_chars == 0,
        "no_boilerplate_left": boiler == 0,
        "has_paragraphs": paragraphs >= 2,
    }
    ok = all(checks.values())

    size_desc = f"{cjk_chars} 汉字" if is_cjk else f"{words} words"
    print(f"篇幅: {size_desc} | 段落: {paragraphs} | 异常字符: {bad_chars} | 残留站名: {boiler}")
    for k, v in checks.items():
        print(f"  {'OK ' if v else 'BAD'} {k}")

    dest.mkdir(parents=True, exist_ok=True)
    src.mkdir(parents=True, exist_ok=True)
    # newline="" 避免 Windows 把已有的 \r\n 再转成 \r\r\n
    (src / "raw.txt").write_text(raw_text, encoding="utf-8", newline="")

    if not ok:
        print("[FAIL] 校验未通过，未写入 original.txt", file=sys.stderr)
        return 2

    (src / "original.txt").write_text(text + "\n", encoding="utf-8", newline="\n")

    meta = {
        "title": args.title,
        "title_source": book["title"],
        "author": args.author or ", ".join(a["name"] for a in book.get("authors", [])),
        "language": lang,
        "script": "simplified" if converted else ("traditional" if is_cjk else "latin"),
        "source_type": "project_gutenberg",
        "source": url,
        "gutenberg_id": book["id"],
        "fetched_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "stats": {
            "words": words,
            "chars": len(text),
            "cjk_chars": cjk_chars,
            "paragraphs": paragraphs,
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        },
        "verification": checks,
        "note": "Project Gutenberg 公版文本；译文/校点版权另计。",
    }
    (dest / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    print(f"[OK] 已写入 {src / 'original.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
