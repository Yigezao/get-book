import re
from bs4 import BeautifulSoup
files=['xiaoxiao','zhangfu','shoujie','danao','panxiansheng','chaoren','shangrenfu','duanhun','yueyaer','huawei','zaisi','shafei','meiyu','xiaoerhei','hehuading','chenhuan','oxiangxue','qingpingwan','muzhikao','shibasui']
for f in files:
    raw=open(f'pages/{f}.html','rb').read()
    for enc in ('gb18030','utf-8','big5'):
        try: s=raw.decode(enc); break
        except: pass
    soup=BeautifulSoup(s,'html.parser')
    for tag in soup(['script','style']): tag.decompose()
    t=''.join(l.strip() for l in soup.get_text('\n').split('\n') if l.strip())
    print('='*10,f,'cjk',len(re.findall(r'[\u4e00-\u9fff]',t)))
    print(' TAIL',repr(t[-110:]))
