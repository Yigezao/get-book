import re
from bs4 import BeautifulSoup
jobs=[('more2/daoliu_sohu.html','utf-8','article#mp-editor'),('more2/mingruo_163.html','utf-8','div.post_body'),('more2/xigua_sohu.html','utf-8','article#mp-editor'),('more2/xigua_wansong.html','utf-8','div.content'),('more2/guiqulai_5156.html','gb18030','td.font_15')]
for fn,enc,sel in jobs:
    s=open(fn,'rb').read().decode(enc,'replace')
    node=BeautifulSoup(s,'html.parser').select_one(sel)
    t='\n'.join(l.strip() for l in node.get_text('\n').split('\n') if l.strip()) if node else ''
    print('='*12,fn,sel,'cjk',len(re.findall(r'[\u4e00-\u9fff]',t)))
    print(' HEAD',repr(t[:120])); print(' TAIL',repr(t[-120:]))
