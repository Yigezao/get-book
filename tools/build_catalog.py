#!/usr/bin/env python3
"""重排 Books/：给每本书加序号前缀，并生成 Books/总目录.txt。

用法:
    python tools/build_catalog.py

规则:
    中文作品 → 日文作品 → 外文作品；组内按作者、书名排序。
    已有 "数字_" 前缀会先剥掉再重新编号，可重复运行。
"""

import hashlib
import json
import re
import shutil
from datetime import date
from pathlib import Path

from pypinyin import lazy_pinyin

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "Books"
CJK_RE = re.compile(r"[一-鿿]")
JP_RE = re.compile(r"[一-鿿ぁ-んァ-ヶー]")
LANG_LABEL = {"zh": "中文", "ja": "日文", "en": "英文", "fr": "法文", "de": "德文", "pl": "波兰文"}
GROUP_ORDER = ["中文", "日文", "外文"]


def lang_norm(lang: str) -> str:
    l = (lang or "").lower().replace("_", "-")
    if l.startswith("zh"):
        return "zh"
    if l.startswith("ja"):
        return "ja"
    return l


def group_of(lang: str) -> str:
    l = lang_norm(lang)
    if l == "zh":
        return "中文"
    if l == "ja":
        return "日文"
    return "外文"


def pinyin(s: str) -> str:
    return "".join(lazy_pinyin(s)).casefold()


def count_of(text: str, lang: str) -> tuple[int, str]:
    lang = lang_norm(lang)
    if lang == "zh":
        return len(CJK_RE.findall(text)), "字"
    if lang == "ja":
        return len(JP_RE.findall(text)), "字"
    return len(text.split()), "词"


def main() -> int:
    records = []
    for d in BOOKS.iterdir():
        if not d.is_dir() or d.name.startswith("."):
            continue
        meta_path = d / "meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        title = re.sub(r"^\d+_", "", meta.get("title") or d.name)
        author = meta.get("author", "")
        lang = lang_norm(meta.get("language", "zh"))
        text_path = d / "source" / "original.txt"
        text = text_path.read_text(encoding="utf-8") if text_path.exists() else ""
        count, unit = count_of(text, lang)
        records.append(
            {
                "old": d,
                "title": title,
                "author": author,
                "lang": lang,
                "group": group_of(lang),
                "count": count,
                "unit": unit,
                "meta": meta,
                "text": text,
            }
        )

    records.sort(
        key=lambda r: (
            GROUP_ORDER.index(r["group"]),
            pinyin(r["author"]),
            pinyin(r["title"]),
        )
    )
    for i, r in enumerate(records, 1):
        r["index"] = i
        r["new"] = f"{i}_{r['title']}"

    # 两段式改名，避免 a→b 撞名
    for r in records:
        tmp = BOOKS / f".tmp_catalog_{r['index']}"
        if tmp.exists():
            raise SystemExit(f"临时目录已存在: {tmp}")
        r["old"].rename(tmp)
        r["tmp"] = tmp
    for r in records:
        final = BOOKS / r["new"]
        r["tmp"].rename(final)
        # 更新 meta 统计与目录号
        meta = r["meta"]
        meta.setdefault("stats", {})
        text = r["text"]
        meta["stats"]["chars"] = len(text)
        meta["stats"]["paragraphs"] = len([p for p in text.split("\n\n") if p.strip()])
        meta["stats"]["sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if r["lang"] == "zh":
            meta["stats"]["cjk_chars"] = r["count"]
        elif r["lang"] == "ja":
            meta["stats"]["japanese_chars"] = r["count"]
        else:
            meta["stats"]["words"] = r["count"]
        meta["catalog"] = {"index": r["index"], "folder": r["new"], "group": r["group"]}
        (final / "meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
        )

    counts = {g: sum(1 for r in records if r["group"] == g) for g in GROUP_ORDER}
    lines = [
        "Get_book 藏书目录",
        f"更新：{date.today().isoformat()}",
        f"共 {len(records)} 本：中文 {counts['中文']}、日文 {counts['日文']}、外文 {counts['外文']}",
        "",
    ]
    for g in GROUP_ORDER:
        lines.append(f"【{g}】")
        for r in records:
            if r["group"] != g:
                continue
            label = LANG_LABEL.get(r["lang"], r["lang"])
            lines.append(f"{r['new']} | {r['author']} | {label} {r['count']:,} {r['unit']}")
        lines.append("")
    incomplete = ROOT / "_work" / "incomplete"
    if incomplete.exists() and any(incomplete.iterdir()):
        names = "、".join(p.name for p in incomplete.iterdir() if p.is_dir())
        lines += ["", f"注：缺章未入藏：{names}（暂存 _work/incomplete/）"]
    (BOOKS / "总目录.txt").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")

    # 同步纯文本全文：TXT全文/<编号_书名>.txt
    txt_dir = ROOT / "TXT全文"
    txt_dir.mkdir(exist_ok=True)
    current = set()
    for r in records:
        src = BOOKS / r["new"] / "source" / "original.txt"
        dst = txt_dir / f"{r['new']}.txt"
        shutil.copyfile(src, dst)
        current.add(dst.name)
    # 清掉上一次生成、但这次不在目录里的编号文件（不动用户自己放的 txt）
    for f in txt_dir.glob("*.txt"):
        if re.match(r"^\d+_", f.name) and f.name not in current:
            f.unlink()

    print(f"完成：{len(records)} 本；目录已写入 {BOOKS / '总目录.txt'}")
    print(f"TXT 全文已同步：{len(current)} 个 -> {txt_dir}")
    for g in GROUP_ORDER:
        print(f"  {g}: {counts[g]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
