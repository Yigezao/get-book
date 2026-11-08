import re
from pathlib import Path
files=[
 "Monday or Tuesday.txt","Winesburg, Ohio.txt","Twice-Told Tales/source/original.txt",
 "All the Sad Young Men/source/original.txt","Men Without Women/source/original.txt",
 "Twain Bank Note Stories/source/original.txt","Contes du lundi/source/original.txt",
 "Love of Life and Other Stories/source/original.txt","The Queen of Spades and Other Stories/source/original.txt",
 "The Mantle and Other Stories/source/original.txt",
]
for fn in files:
    t=Path(fn).read_text(encoding='utf-8',errors='replace')
    print('='*14,fn)
    for i,l in enumerate(t.split('\n')):
        s=l.strip()
        if not s or len(s)>60: continue
        letters=[c for c in s if c.isalpha()]
        if len(letters)<4: continue
        up=sum(1 for c in letters if c.isupper())/len(letters)
        if up>0.85 and not re.search(r'[.,;:!?]$',s):
            print(' ',i,s[:55])
