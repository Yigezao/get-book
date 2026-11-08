import json,re
from pathlib import Path
for d in sorted(Path('Books').iterdir()):
    f=d/'source'/'original.txt'
    if not f.exists(): continue
    t=f.read_text(encoding='utf-8')
    ps=[p for p in t.split('\n\n') if p.strip()]
    m=json.loads((d/'meta.json').read_text(encoding='utf-8')) if (d/'meta.json').exists() else {}
    cjk=len(re.findall(r'[\u4e00-\u9fff]',t))
    bad=[k for k in ['提示','张宝华','宇慧编后按','编后按','作者简介','文学视界','中国读书网','扫描','校对'] if k in t]
    print(f'{d.name:<14} cjk={cjk:>6} 段={len(ps):>3} 首={ps[0][:16]!r} 尾={ps[-1][-18:]!r} 残留={bad}')
