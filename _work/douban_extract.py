import json,re
from bs4 import BeautifulSoup
for src,out in [('t_ds.html','more/duoshou.txt'),('more3/xigua_douban.html','more/xigua_douban.txt')]:
    s=open(src,'rb').read().decode('utf-8','replace')
    soup=BeautifulSoup(s,'html.parser')
    got=None
    for sc in soup.find_all('script',type='application/ld+json'):
        try: d=json.loads(sc.string or '')
        except: continue
        if isinstance(d,dict) and d.get('text'):
            got=d['text']; break
    if got:
        open(out,'w',encoding='utf-8',newline='\n').write(got)
        print(out,'chars',len(got),'cjk',len(re.findall(r'[\u4e00-\u9fff]',got)))
        print(' HEAD',repr(got[:80])); print(' TAIL',repr(got[-100:]))
    else: print(src,'no ld+json text')
