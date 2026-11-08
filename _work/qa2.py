import json,re
from pathlib import Path
bad_words=['提示','参考答案','试题','阅读练习','赏析','编辑整理','扫描','校对','文学视界','中国读书网','天方有声','责任编辑']
rows=[]
for d in sorted(Path('Books').iterdir()):
    f=d/'source'/'original.txt'
    if not f.exists(): continue
    t=f.read_text(encoding='utf-8'); ps=[p for p in t.split('\n\n') if p.strip()]
    cjk=len(re.findall(r'[\u4e00-\u9fff]',t))
    bad=[w for w in bad_words if w in t]
    rows.append((d.name,cjk,len(ps),ps[0][:12],ps[-1][-22:],bad))
for r in rows:
    print(f'{r[0]:<12} {r[1]:>6}字 {r[2]:>3}段 首={r[3]!r:<14} 尾={r[4]!r:<26} 残留={r[5]}')
print('总计',len(rows),'篇')
