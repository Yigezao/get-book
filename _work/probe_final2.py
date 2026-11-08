import re
from bs4 import BeautifulSoup
def body(fn,enc,sel):
    s=open(fn,'rb').read().decode(enc,'replace')
    n=BeautifulSoup(s,'html.parser').select_one(sel)
    return '\n'.join(l.strip() for l in n.get_text('\n').split('\n') if l.strip())
t=body('more2/daoliu_sohu.html','utf-8','article#mp-editor')
print('=== 倒流河 贾平凹 positions',[m.start() for m in re.finditer('贾平凹',t)][-5:],'len',len(t))
print(t[-1300:])
t2=body('more2/mingruo_163.html','utf-8','div.post_body')
print('=== 命若琴弦 starts',t2.find('莽莽苍苍'),'date',t2.find('1985年4月20日'),'len',len(t2))
print(t2[:500]); print('...'); print(t2[-400:])
t3=body('more2/guiqulai_5156.html','gb18030','td.font_15')
print('=== 归去来 2200-2700'); print(t3[2150:2700])
s=open('t_ds.html','rb').read().decode('utf-8','replace')
t4='\n'.join(l.strip() for l in BeautifulSoup(s,'html.parser').get_text('\n').split('\n') if l.strip())
print('=== 多收 tail',repr(t4[-500:]))
