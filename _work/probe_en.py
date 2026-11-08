from pathlib import Path
jobs=[
 ("Monday or Tuesday.txt","THE MARK ON THE WALL"),
 ("Winesburg, Ohio.txt","HANDS"),
 ("Twice-Told Tales/source/original.txt","THE MINISTER'S BLACK VEIL"),
 ("All the Sad Young Men/source/original.txt","WINTER DREAMS"),
 ("Men Without Women/source/original.txt","HILLS LIKE WHITE ELEPHANTS"),
 ("Twain Bank Note Stories/source/original.txt","BANK-NOTE"),
 ("Contes du lundi/source/original.txt","DERNIÈRE CLASSE"),
 ("Love of Life and Other Stories/source/original.txt","LOVE OF LIFE"),
 ("The Queen of Spades and Other Stories/source/original.txt","STATION"),
 ("The Mantle and Other Stories/source/original.txt","MANTLE"),
]
for fn,key in jobs:
    p=Path(fn)
    t=p.read_text(encoding='utf-8',errors='replace')
    lines=t.split('\n')
    hits=[i for i,l in enumerate(lines) if key.lower() in l.lower()]
    print('='*12,fn,'| key',key,'| hits',hits[:8],'| lines',len(lines))
    for i in hits[:2]:
        print('  ---',i)
        for j in range(max(0,i-2),min(len(lines),i+8)):
            s=lines[j].strip()
            if s: print('   ',j,repr(s[:90]))
