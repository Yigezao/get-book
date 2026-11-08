import re
from bs4 import BeautifulSoup
files=['daoliu_sohu','mingruo_163','xigua_sohu','xigua_wansong','guiqulai_5156','guiqulai_dushu']
for k in files:
    raw=open(f'more2/{k}.html','rb').read()
    best=(None,0,'')
    for enc in ('utf-8','gb18030','big5'):
        try:
            s=raw.decode(enc); t='\n'.join(l.strip() for l in BeautifulSoup(s,'html.parser').get_text('\n').split('\n') if l.strip())
            cjk=len(re.findall(r'[\u4e00-\u9fff]',t))
            if cjk>best[1]: best=(enc,cjk,t)
        except: pass
    enc,cjk,t=best
    print('='*15,k,'cjk',cjk)
    print(' HEAD',repr(t[:130])); print(' TAIL',repr(t[-130:]))
    print(' keys',{x:(x in t) for x in ['老笨','鸡蛋','莽莽苍苍','无所谓从哪儿来','陈素珍','福三','黄治先','四妹子','马眼镜','万盛米行','旧毡帽']})
