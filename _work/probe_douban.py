import re
from bs4 import BeautifulSoup
for fn,phrase in [('t_ds.html','万盛米行的河埠头'),('more3/xigua_douban.html','陈素珍')]:
    s=open(fn,'rb').read().decode('utf-8','replace')
    soup=BeautifulSoup(s,'html.parser')
    node=soup.find(string=re.compile(phrase))
    print('='*12,fn,'node?',bool(node))
    if node:
        p=node.parent
        for _ in range(6):
            print('  ',p.name,'class=',p.get('class'),'id=',p.get('id'))
            p=p.parent
            if p is None: break
    i=s.find(phrase); print('  raw idx',i); print(repr(s[max(0,i-200):i+100]))
