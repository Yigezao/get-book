import re
from bs4 import BeautifulSoup
def text_of(f):
    raw=open(f'pages/{f}.html','rb').read()
    for enc in ('gb18030','utf-8','big5'):
        try: s=raw.decode(enc); break
        except: pass
    soup=BeautifulSoup(s,'html.parser')
    for tag in soup(['script','style']): tag.decompose()
    return '\n'.join(l.strip() for l in soup.get_text('\n').split('\n') if l.strip())
for f in ['panxiansheng','zaisi','meiyu']:
    t=text_of(f)
    print('='*20,f)
    i=max(t.rfind('（张宝华）'), t.rfind('***'))
    print('marker at',i,'of',len(t))
    print(t[max(0,i-1600):i+40])
