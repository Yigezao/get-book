import re
from bs4 import BeautifulSoup
s=open('pages/shoujie.html','rb').read().decode('gb18030')
print('pre tags', s.lower().count('<pre'), 'p', s.lower().count('<p'), 'br', s.lower().count('<br'))
i=s.find('明海')
print('idx',i)
print(repr(s[i-200:i+300]))
soup=BeautifulSoup(s,'html.parser')
t=soup.get_text('\n')
lines=t.split('\n')
print('total lines',len(lines),'empty',sum(1 for l in lines if not l.strip()))
for j,l in enumerate(lines[10:40],10): print(j,repr(l[:60]))
