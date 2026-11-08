import re
from pathlib import Path
jobs=[
 ("All the Sad Young Men/source/original.txt",684),
 ("Men Without Women/source/original.txt",1092),
 ("Twain Bank Note Stories/source/original.txt",100),
 ("Contes du lundi/source/original.txt",122),
 ("Love of Life and Other Stories/source/original.txt",12),
 ("The Queen of Spades and Other Stories/source/original.txt",200),
 ("The Mantle and Other Stories/source/original.txt",24),
]
for fn,start in jobs:
    t=Path(fn).read_text(encoding='utf-8',errors='replace')
    print('='*14,fn)
    n=0
    for i,l in enumerate(t.split('\n')):
        if i<=start: continue
        s=l.strip()
        if not s or len(s)>70: continue
        letters=[c for c in s if c.isalpha()]
        if len(letters)<4: continue
        up=sum(1 for c in letters if c.isupper())/len(letters)
        if up>0.8 and not re.search(r'[.,;:!?]$',s):
            print(' ',i,s[:60]); n+=1
            if n>=12: break
