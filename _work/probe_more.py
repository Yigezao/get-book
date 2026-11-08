import re
from bs4 import BeautifulSoup
for k in ['baihehua','maizi','daoliuhe','mingruo']:
    raw=open(f'more/{k}.html','rb').read()
    best=None
    for enc in ('utf-8','gb18030','big5'):
        try:
            s=raw.decode(enc)
            t='\n'.join(l.strip() for l in BeautifulSoup(s,'html.parser').get_text('\n').split('\n') if l.strip())
            cjk=len(re.findall(r'[\u4e00-\u9fff]',t))
            if best is None or cjk>best[1]: best=(enc,cjk,t,s)
        except: pass
    enc,cjk,t,s=best
    print('='*15,k,'cjk',cjk)
    print(' HEAD',repr(t[:150])); print(' TAIL',repr(t[-150:]))
    print(' keys',{x:(x in t) for x in ['百合花的被子','老家的麦地','倒流河','莽莽苍苍','救救孩子','万盛米行','陈素珍','建敏','顺顺']})
