s=open('tmp_ad8031.html',encoding='utf-8').read()
pos=[]; i=s.find('在沪上闲居')
while i>=0: pos.append(i); i=s.find('在沪上闲居',i+1)
print('positions',pos)
for p in pos[1:2]:
    print(s[max(0,p-1200):p+300])
print('--- div classes near body ---')
import re
for m in re.finditer(r'<div[^>]*(class|id)="[^"]*(content|article|txt|main)[^"]*"[^>]*>',s):
    print(m.group(0)[:200])
