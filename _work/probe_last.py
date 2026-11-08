import re
from bs4 import BeautifulSoup
for fn,phrase in [('more/baihehua.html','一九四六年的中秋'),('more/maizi.html','建敏是福来酒家')]:
    raw=open(fn,'rb').read(); s=raw.decode('gb18030','replace')
    soup=BeautifulSoup(s,'html.parser')
    node=soup.find(string=re.compile(phrase)); print('='*10,fn,bool(node))
    if node:
        p=node.parent
        for _ in range(5):
            print('  ',p.name,'class=',p.get('class'),'id=',p.get('id')); p=p.parent
            if p is None: break
