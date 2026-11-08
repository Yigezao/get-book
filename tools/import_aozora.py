#!/usr/bin/env python3
"""青空文库 HTML → 纯文本。去掉 ruby 注音，保留正文。"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup

JP_RE = re.compile(r"[一-鿿ぁ-んァ-ヶー]")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--author", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--min-chars", type=int, default=500)
    args = ap.parse_args()

    raw = Path(args.file).read_bytes()
    for enc in ("shift_jis", "utf-8", "euc-jp"):
        try:
            html = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        html = raw.decode("shift_jis", errors="replace")

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["rt", "rp", "script", "style", "div.metadata", "div.notes", "ol.notes"]):
        tag.decompose()
    for br in soup.find_all("br"):
        br.replace_with("\n")
    node = soup.select_one("div.main_text") or soup.body or soup
    lines = [ln.replace("　", " ").strip() for ln in node.get_text("\n").split("\n")]
    paras = [ln for ln in lines if ln]
    body = args.title + "\n\n" + "\n\n".join(paras)

    jp = len(JP_RE.findall(body))
    checks = {
        "starts_with_title": body.startswith(args.title),
        "min_chars": jp >= args.min_chars,
        "has_paragraphs": len(paras) >= 3,
    }
    print(f"=== {args.title}: {jp} 日文字 / {len(paras)} 段")
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
        "language": "ja",
        "script": "japanese",
        "source_type": "aozora_bunko",
        "source": args.source,
        "fetched_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "stats": {
            "chars": len(body),
            "japanese_chars": jp,
            "paragraphs": len(paras),
            "sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        },
        "verification": checks,
        "note": "青空文库公版原文；ruby 注音已去除。",
    }
    (dest / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    print(f"[OK] {dest / 'source' / 'original.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
