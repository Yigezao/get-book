import json
import re

from bs4 import BeautifulSoup

for src, out in [("t_ds.html", "more/duoshou.txt"), ("more3/xigua_douban.html", "more/xigua_douban.txt")]:
    s = open(src, "rb").read().decode("utf-8", "replace")
    soup = BeautifulSoup(s, "html.parser")
    got = None
    for sc in soup.find_all("script", type="application/ld+json"):
        txt = sc.get_text()
        try:
            d = json.loads(txt)
        except Exception:
            continue
        if isinstance(d, dict) and d.get("text"):
            got = d["text"]
            break
    if not got:
        print(src, "no text")
        continue
    got = got.replace("\\r\\n", "\n").replace("\\n", "\n")
    open(out, "w", encoding="utf-8", newline="\n").write(got)
    print(out, "chars", len(got), "cjk", len(re.findall(r"[一-鿿]", got)))
    print(" HEAD", repr(got[:90]))
    print(" TAIL", repr(got[-120:]))
