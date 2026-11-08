#!/usr/bin/env python3
"""从已抓取的文集里按篇名拆出单篇。

用法:
    python tools/split_stories.py --collection Books/彷徨 --pick 祝福,伤逝,在酒楼上
    python tools/split_stories.py --collection Books/呐喊 --pick 孔乙己,狂人日记

边界按**文件里的实际顺序**取下一篇，不按目录顺序（古腾堡版篇序可能是乱的）。
篇名表见 tools/collections.json；缺篇会明确报错，不会把上一篇的尾巴当成正文。
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CJK_RE = re.compile(r"[㐀-䶿一-鿿豈-﫿]")


def load_titles(collection_name: str) -> list[str]:
    p = HERE / "collections.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    return data.get(collection_name, [])


def title_index(paras: list[str], title: str) -> int | None:
    """匹配独立成段的篇名，允许末尾带【1】〔1〕或副标题。"""
    pat = re.compile(rf"^{re.escape(title)}(?:[【〔\[]\d+[】〕\]]|[\s　]+|$)")
    for i, p in enumerate(paras):
        if pat.match(p.strip()):
            return i
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--collection", required=True, help="文集目录，如 Books/彷徨")
    ap.add_argument("--pick", required=True, help="要拆出的篇名，逗号分隔")
    ap.add_argument("--out", default=None, help="输出根目录，默认 Books/")
    ap.add_argument("--min-chars", type=int, default=500, help="低于此汉字数视为失败")
    args = ap.parse_args()

    col = Path(args.collection)
    src_file = col / "source" / "original.txt"
    col_meta_path = col / "meta.json"
    if not src_file.exists():
        print(f"[FAIL] 找不到 {src_file}", file=sys.stderr)
        return 2

    col_meta = json.loads(col_meta_path.read_text(encoding="utf-8")) if col_meta_path.exists() else {}
    col_name = col_meta.get("title") or col.name
    known = load_titles(col_name)
    if not known:
        print(f"[FAIL] tools/collections.json 里没有《{col_name}》的篇名表", file=sys.stderr)
        return 2

    text = src_file.read_text(encoding="utf-8")
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]

    # 定位篇名 → 按实际位置排序 → 下一篇即边界
    found = []
    for t in known:
        i = title_index(paras, t)
        if i is not None:
            found.append((i, t))
    found.sort()

    out_root = Path(args.out) if args.out else HERE.parent / "Books"
    picks = [s.strip() for s in args.pick.split(",") if s.strip()]
    missing = [t for t in picks if t not in [x[1] for x in found]]
    if missing:
        print(f"[FAIL] 文集里找不到这些篇目: {', '.join(missing)}", file=sys.stderr)
        return 2

    failed = False
    for i, (idx, name) in enumerate(found):
        if name not in picks:
            continue
        end = found[i + 1][0] if i + 1 < len(found) else len(paras)
        # 保留篇名，丢掉紧随其后的版式行，如“著者：鲁迅”
        start = idx + 1
        while start < end and re.match(r"^(著者|作者)[：:]", paras[start]):
            start += 1
        body = "\n\n".join([paras[idx]] + paras[start:end]).strip("\n")

        cjk = len(CJK_RE.findall(body))
        checks = {
            "starts_with_title": body.split("\n")[0].strip().startswith(name),
            "min_chars": cjk >= args.min_chars,
            "no_boilerplate": not re.search(r"Project Gutenberg|gutenberg\.org|制作[：:]", body, re.I),
            "has_paragraphs": body.count("\n\n") >= 2,
        }
        ok = all(checks.values())
        print(f"=== {name}: {cjk} 汉字 / {body.count(chr(10)+chr(10))+1} 段 / 校验 {'通过' if ok else '失败'}")
        for k, v in checks.items():
            print(f"  {'OK ' if v else 'BAD'} {k}")
        if not ok:
            failed = True
            continue

        dest = out_root / name
        (dest / "source").mkdir(parents=True, exist_ok=True)
        (dest / "source" / "original.txt").write_text(body + "\n", encoding="utf-8", newline="\n")
        meta = {
            "title": name,
            "author": col_meta.get("author", ""),
            "language": col_meta.get("language", "zh"),
            "script": col_meta.get("script", "simplified"),
            "source_type": "collection_extract",
            "source_collection": col_name,
            "source": col_meta.get("source", ""),
            "gutenberg_id": col_meta.get("gutenberg_id"),
            "fetched_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
            "stats": {
                "chars": len(body),
                "cjk_chars": cjk,
                "paragraphs": body.count("\n\n") + 1,
                "sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            },
            "verification": checks,
            "note": f"从《{col_name}》按篇名切出；篇末注释一并保留。",
        }
        (dest / "meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
        )
        print(f"  [OK] {dest / 'source' / 'original.txt'}")

    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
