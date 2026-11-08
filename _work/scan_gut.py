import json,urllib.request,urllib.parse,time
qs=[("fall of the house of usher",None),("rashomon",None),("the metamorphosis",None),("in the penal colony",None),("the mark on the wall",None),("winesburg ohio",None),("the minister's black veil",None),("winter dreams",None),("the last class",None),("the million pound bank note",None),("running for governor",None),("love of life",None),("the stationmaster",None),("the overcoat",None),("a sportsman's sketches",None),("a rose for emily",None),("hills like white elephants",None),("the facts of life",None)]
for q,lang in qs:
    u="https://gutendex.com/books?"+urllib.parse.urlencode({"search":q})
    try:
        d=json.loads(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"x"}),timeout=40).read())
        rs=[b for b in d.get("results",[]) if any(k.startswith("text/plain") for k in b["formats"])]
        print("==",q,"count",d.get("count"))
        for b in rs[:3]:
            print("  ",b["id"],"|",b["title"][:55],"|",[a["name"] for a in b.get("authors",[])][:1],"|",b.get("languages"))
    except Exception as e:
        print("==",q,"ERR",e)
    time.sleep(0.3)
