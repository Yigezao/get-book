#!/usr/bin/env python3
"""把网页/存档页里的单篇正文清洗成标准目录。

用法:
    python tools/import_page.py --file page.html --title 受戒 --author 汪曾祺 \
        --source "https://..." --mode unwrap

支持两种排版:
    unwrap  老式 <pre> 硬换行 + 行首缩进（DACHS/黄金书屋、古腾堡中文）
    lines   一段一个 <p>（中国作家网）

会切掉网页末尾的书目/赏析/校对称谓，校验不过不写 original.txt。
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_gutenberg import CJK_RE, unwrap  # noqa: E402

BOILER = re.compile(
    r"(宇慧文学视界|文学视界|中国读书网|小草扫校|新语丝|编辑整理|扫描校对|独家推出"
    r"|回目录|上一页|下一页|一鸣扫描|雪儿校对|天方有声图书馆|有声数字图书馆|http://|https://|www\.)"
)
# 网页末尾常见的附加内容起点（只在中后段生效，避免误伤正文）
CUT_MARKERS = [
    "\n提示",
    "【编后按",
    "【作者简介",
    "小说、散文集《超人》。",
    "《陈奂生上城》作者高晓声",
    "宇慧编后按",
    "【文学视界",
    "此文章由",
    "\n***",
    "\n------------------",
    "\n☆",
]
LEAD_DROP = re.compile(
    r"(^作者[：:]|^著者[：:]|^黄金书屋|^回目录$|^上一页$|^下一页$"
    r"|^《?[^》]{1,20}》?自序$)"
)


def decode(raw: bytes) -> tuple[str, str]:
    for enc in ("utf-8-sig", "utf-8", "gb18030", "big5"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace"), "utf-8?"


def norm(s: str) -> str:
    s = re.sub(r"^黄金书屋---", "", s)
    s = re.sub(r"[\s　《》〈〉()（）]", "", s)
    return s.casefold()


def extract(path: Path, selector: str | None) -> tuple[str, str]:
    raw = path.read_bytes()
    text, enc = decode(raw)
    soup = BeautifulSoup(text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    if selector:
        node = soup.select_one(selector)
        if node is None:
            raise SystemExit(f"[FAIL] 选择器没匹配到: {selector}")
        content = node.get_text("\n")
    else:
        content = soup.get_text("\n")
    content = content.replace("\r\n", "\n").replace("\r", "\n").replace("\xa0", " ")
    return content, enc


def cut_tail(text: str) -> str:
    """从中后段开始找附加内容标记，切掉。"""
    n = len(text)
    for m in CUT_MARKERS:
        idx = text.find(m)
        if idx > n * 0.35:
            text = text[:idx]
    return text


def clean_lines(text: str, title: str, author: str) -> list[str]:
    lines = [ln.rstrip() for ln in text.split("\n")]
    # 去掉网页导航/版权行，但保留空行用来分段
    lines = [ln for ln in lines if not (ln.strip() and BOILER.search(ln))]
    # 去掉孤立的装饰行/残留括号
    lines = [ln for ln in lines if not re.fullmatch(r"\s*(?:[-*—]{3,}|【|】|〖|〗|☆+)\s*", ln)]
    # 去掉开头重复书名、作者行、版式行
    nt, na = norm(title), norm(author)
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        ns = norm(s)
        if (
            LEAD_DROP.search(s)
            or (nt and ns == nt)
            or (nt and ns.startswith(nt) and len(ns) <= len(nt) + 12)
            or (na and ns == na)
        ):
            i += 1
            continue
        break
    return lines[i:]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--author", default="")
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--selector", default=None, help="CSS 选择器，如 div.end_article")
    ap.add_argument("--mode", choices=["unwrap", "lines"], default="unwrap")
    ap.add_argument("--min-chars", type=int, default=500)
    ap.add_argument("--min-words", type=int, default=150)
    ap.add_argument("--lang", default=None, help="语言标记，默认按汉字比例判断")
    ap.add_argument("--cut", action="append", default=[], help="额外的正文结束标记（可多次）")
    ap.add_argument("--cut-last", action="append", default=[], help="按最后一次出现的位置切（用于目录与正文重名的篇名）")
    ap.add_argument("--start", default=None, help="从该标记处开始截取正文（跳过网页页眉/作者简介）")
    ap.add_argument("--end-trim", default=None, help="正文末尾要剥掉的后缀字符")
    args = ap.parse_args()

    path = Path(args.file)
    text, enc = extract(path, args.selector)
    if args.start:
        idx = text.find(args.start)
        if idx >= 0:
            text = text[idx:]
    for marker in args.cut:
        idx = text.find(marker)
        if idx >= 0:
            text = text[:idx]
    for marker in args.cut_last:
        idx = text.rfind(marker)
        if idx >= 0:
            text = text[:idx]
    text = cut_tail(text)
    lines = clean_lines(text, args.title, args.author)

    if args.mode == "lines":
        body = "\n\n".join(ln.strip() for ln in lines if ln.strip())
    else:
        body = unwrap("\n".join(lines))
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    body = re.sub(r"(?:\n+)?提示[：:]?\s*$", "", body).rstrip()
    if args.end_trim and body.endswith(args.end_trim):
        body = body[: -len(args.end_trim)].rstrip()
    if args.author:
        parts = [x for x in body.split("\n\n") if x.strip()]
        while parts and norm(parts[-1]) == norm(args.author):
            parts.pop()
        body = "\n\n".join(parts)
    if not body.startswith(args.title):
        body = args.title + "\n\n" + body

    cjk = len(CJK_RE.findall(body))
    words = len(body.split())
    paras = len([p for p in body.split("\n\n") if p.strip()])
    is_cjk = cjk / max(1, len(re.sub(r"\s", "", body))) > 0.2
    checks = {
        "starts_with_title": norm(body.split("\n")[0]).startswith(norm(args.title)),
        "min_length": (cjk >= args.min_chars) if is_cjk else (words >= args.min_words),
        "no_boilerplate": not BOILER.search(body),
        "has_paragraphs": paras >= 2,
    }
    print(f"=== {args.title}: {cjk} 汉字 / {words} words / {paras} 段 / 编码 {enc}")
    for k, v in checks.items():
        print(f"  {'OK ' if v else 'BAD'} {k}")
    if not all(checks.values()):
        print("[FAIL] 校验未通过，未写入", file=sys.stderr)
        return 2

    out_root = Path(args.out) if args.out else Path(__file__).resolve().parent.parent / "Books"
    dest = out_root / args.title
    (dest / "source").mkdir(parents=True, exist_ok=True)
    (dest / "source" / "original.txt").write_text(body + "\n", encoding="utf-8", newline="\n")
    meta = {
        "title": args.title,
        "author": args.author,
        "language": args.lang or ("zh" if is_cjk else "en"),
        "script": "simplified" if is_cjk else "latin",
        "source_type": "web_archive",
        "source": args.source,
        "fetched_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "stats": {
            "chars": len(body),
            "cjk_chars": cjk,
            "paragraphs": paras,
            "sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        },
        "verification": checks,
        "note": "公开学术存档/官网文本；仅个人学习使用。",
    }
    (dest / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    print(f"[OK] {dest / 'source' / 'original.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
