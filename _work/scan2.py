import json
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

QUERIES = [
    ("fall of the house of usher", None),
    ("the metamorphosis", None),
    ("verwandlung", "de"),
    ("in the penal colony", None),
    ("the mark on the wall", None),
    ("winesburg ohio", None),
    ("the minister's black veil", None),
    ("winter dreams", None),
    ("the last class", None),
    ("the million pound bank note", None),
    ("running for governor", None),
    ("love of life", None),
    ("the stationmaster", None),
    ("the overcoat", None),
    ("a sportsman's sketches", None),
    ("a rose for emily", None),
    ("hills like white elephants", None),
    ("the facts of life", None),
]


def one(q, lang):
    params = {"search": q}
    if lang:
        params["languages"] = lang
    url = "https://gutendex.com/books?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "x"})
        d = json.loads(urllib.request.urlopen(req, timeout=30).read())
        rs = [b for b in d.get("results", []) if any(k.startswith("text/plain") for k in b["formats"])]
        return q, d.get("count"), [
            (b["id"], b["title"][:60], [a["name"] for a in b.get("authors", [])][:1], b.get("languages"))
            for b in rs[:3]
        ]
    except Exception as e:
        return q, "ERR", str(e)


with ThreadPoolExecutor(max_workers=6) as ex:
    futs = [ex.submit(one, q, l) for q, l in QUERIES]
    for f in as_completed(futs):
        q, c, r = f.result()
        print("==", q, "count", c, flush=True)
        if isinstance(r, list):
            for x in r:
                print("  ", x, flush=True)
        else:
            print("  ", r, flush=True)
