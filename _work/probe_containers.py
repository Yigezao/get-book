import re
from bs4 import BeautifulSoup
def find(fn,enc,phrase):
    s=open(fn,'rb').read().decode(enc,'replace')
    soup=BeautifulSoup(s,'html.parser')
    node=soup.find(string=re.compile(phrase))
    print('='*10,fn,'found',bool(node))
    if node:
        p=node.parent
        for _ in range(5):
            print('  ',p.name, 'class=',p.get('class'),'id=',p.get('id'))
            p=p.parent
            if p is None: break
for args in [('more2/daoliu_sohu.html','utf-8','有一条倒流河'),('more2/mingruo_163.html','utf-8','莽莽苍苍的群山'),('more2/xigua_sohu.html','utf-8','陈素珍'),('more2/xigua_wansong.html','utf-8','陈素珍'),('more2/guiqulai_5156.html','gb18030','黄治先')]:
    find(*args)
