import re
from bs4 import BeautifulSoup
# 豆瓣 多收
s=open('t_ds.html','rb').read().decode('utf-8','replace')
soup=BeautifulSoup(s,'html.parser')
t='\n'.join(l.strip() for l in soup.get_text('\n').split('\n') if l.strip())
print('DOUBAN cjk',len(re.findall(r'[\u4e00-\u9fff]',t)))
i=t.find('万盛米行'); print(' idx',i); print(repr(t[max(0,i-100):i+300]) if i>=0 else 'no')
# 归去来 5156 分界
s=open('more2/guiqulai_5156.html','rb').read().decode('gb18030','replace')
node=BeautifulSoup(s,'html.parser').select_one('td.font_15')
t='\n'.join(l.strip() for l in node.get_text('\n').split('\n') if l.strip())
for kw in ['下列对','（1）','6．','7．','四妹子','为什么回来']:
    print('归去来',kw,[m.start() for m in re.finditer(re.escape(kw),t)][-3:])
print('归去来 len',len(t)); print('TAIL:',repr(t[-700:]))
