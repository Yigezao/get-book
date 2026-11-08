from bs4 import BeautifulSoup
for f in ['zaisi','meiyu','panxiansheng']:
    raw=open(f'pages/{f}.html','rb').read()
    for enc in ('gb18030','utf-8','big5'):
        try: s=raw.decode(enc); break
        except: pass
    t=BeautifulSoup(s,'html.parser').get_text('\n').replace('\r','')
    i=t.find('张宝华')
    print('='*10,f,'idx',i,'len',len(t))
    print(repr(t[max(0,i-500):i+20]))
