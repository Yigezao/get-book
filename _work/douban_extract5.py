import re

for src, out in [("t_ds.html", "more/duoshou.txt"), ("more3/xigua_douban.html", "more/xigua_douban.txt")]:
    s = open(src, "rb").read().decode("utf-8", "replace")
    b = re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)[0]
    i = b.find('"text"')
    start = b.find('"', i + 6) + 1
    j = start
    while j < len(b):
        if b[j] == '"':
            k, n = j - 1, 0
            while k >= start and b[k] == "\\":
                n += 1
                k -= 1
            if n % 2 == 0:
                break
        j += 1
    text = b[start:j]
    text = text.replace('\\r\\n', '\n').replace('\\n', '\n').replace('\\r', '')
    text = text.replace('\\"', '"').replace('\\/', '/')
    open(out, "w", encoding="utf-8", newline="\n").write(text)
    print(out, "chars", len(text), "cjk", len(re.findall(r"[一-鿿]", text)))
    print(" HEAD", repr(text[:90]))
    print(" TAIL", repr(text[-140:]))
