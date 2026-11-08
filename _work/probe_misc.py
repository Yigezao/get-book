import re
from bs4 import BeautifulSoup
# 豆瓣 多收 container
s=open('t_ds.html','rb').read().decode('utf-8','replace')
soup=BeautifulSoup(s,'html.parser')
node=soup.find(string=re.compile('万盛米行的河埠头'))
print('=== 多收 ancestors')
p=node.parent
for _ in range(6):
    print(' ',p.name,'class=',p.get('class'),'id=',p.get('id')); p=p.parent
    if p is None: break
# 万松浦 分页
s2=open('more2/xigua_wansong.html','rb').read().decode('utf-8','replace')
soup2=BeautifulSoup(s2,'html.parser')
print('=== 万松浦 links with 西瓜/下一页')
for a in soup2.find_all('a'):
    tx=a.get_text(' ',strip=True); h=a.get('href','')
    if any(k in tx for k in ['下一页','下一','西瓜']) or 'page' in h.lower():
        print(' ',tx[:20],'->',h)
print('=== 万松浦 content tail'); 
n=soup2.select_one('div.content'); print(repr(n.get_text('\n')[-300:]) if n else 'none')
