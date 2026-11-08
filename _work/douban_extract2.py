import json,re
for src,out in [('t_ds.html','more/duoshou.txt'),('more3/xigua_douban.html','more/xigua_douban.txt')]:
    s=open(src,'rb').read().decode('utf-8','replace')
    m=re.search(r'"text"\s*:\s*"((?:[^"\]|\.)*)"',s,re.S)
    if not m:
        print(src,'no text field'); continue
    try:
        got=json.loads('"'+m.group(1)+'"')
    except Exception as e:
        print('decode fail',e); continue
    got=got.replace('\r\n','\n').replace('\n','\n')
    open(out,'w',encoding='utf-8',newline='\n').write(got)
    print(out,'chars',len(got),'cjk',len(re.findall(r'[\u4e00-\u9fff]',got)))
    print(' HEAD',repr(got[:90])); print(' TAIL',repr(got[-120:]))
