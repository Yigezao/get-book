import re

for src, out in [("t_ds.html", "more/duoshou.txt"), ("more3/xigua_douban.html", "more/xigua_douban.txt")]:
    s = open(src, "rb").read().decode("utf-8", "replace")
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
    if not blocks:
        print(src, "no block")
        continue
    b = blocks[0]
    i = b.find('"text"')
    if i < 0:
        print(src, "no text key")
        continue
    start = b.find('"', i + 6) + 1
    end = b.rstrip().rfind('"')
    text = b[start:end]
    text = text.replace('\\"', '"').replace('\\n', '\n').replace('\\r', '')
    text = text.replace('\\/', '/')
    open(out, "w", encoding="utf-8", newline="\n").write(text)
    print(out, "chars", len(text), "cjk", len(re.findall(r"[一-鿿]", text)))
    print(" HEAD", repr(text[:90]))
    print(" TAIL", repr(text[-140:]))
