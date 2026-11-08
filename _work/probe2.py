import re
from bs4 import BeautifulSoup
for f in ['oxiangxue','muzhikao']:
    raw=open(f'pages/{f}.html','rb').read()
    for enc in ('gb18030','utf-8','big5'):
        try: s=raw.decode(enc); break
        except: pass
    soup=BeautifulSoup(s,'html.parser')
    for tag in soup(['script','style']): tag.decompose()
    t='\n'.join(l.strip() for l in soup.get_text('\n').split('\n') if l.strip())
    print('='*12,f,'cjk',len(re.findall(r'[\u4e00-\u9fff]',t)))
    print(' HEAD',repr(t[:100])); print(' TAIL',repr(t[-160:]))
print('='*20,'chinawriter structure')
s=open('tmp_ad8031.html',encoding='utf-8').read()
i=s.find('在沪上闲居')
print(s[max(0,i-800):i+200])
