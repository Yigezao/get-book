from bs4 import BeautifulSoup
def text_of(f):
    raw=open(f'pages/{f}.html','rb').read()
    for enc in ('gb18030','utf-8','big5'):
        try: s=raw.decode(enc); break
        except: pass
    soup=BeautifulSoup(s,'html.parser')
    for tag in soup(['script','style']): tag.decompose()
    return '\n'.join(l.strip() for l in soup.get_text('\n').split('\n') if l.strip())
for f in ['hehuading','chenhuan','qingpingwan']:
    t=text_of(f)
    print('='*20,f)
    for kw in ['赏析','鉴赏','作品分析','简析','***','编辑整理','宇慧']:
        pos=[]; i=t.find(kw)
        while i>=0: pos.append(i); i=t.find(kw,i+1)
        if pos: print(' ',kw,pos[-3:])
    print('--- 后半段 ---')
    print(t[-1600:])
