from random import choice, randint, random
from collections import defaultdict

kana = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんアイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
romaji = [
    'a', 'i', 'u', 'e', 'o',
    'ka', 'ki', 'ku', 'ke', 'ko',
    'sa', 'shi', 'su', 'se', 'so',
    'ta', 'chi', 'tsu', 'te', 'to',
    'na', 'ni', 'nu', 'ne', 'no',
    'ha', 'hi', 'fu', 'he', 'ho',
    'ma', 'mi', 'mu', 'me', 'mo',
    'ya', 'yu', 'yo',
    'ra', 'ri', 'ru', 're', 'ro',
    'wa', 'wo', 'n'
]
before_d = defaultdict(int)
before_c = ''
i = 0
with open('kana practicing.txt', 'w', encoding='utf-8') as f:
    while len(kana) > 0:
        selected = choice(kana)
        before_d[selected] += 1
        if before_d[selected] == 4:
            kana = kana.replace(selected, '')
        while selected == before_c and len(kana) > 1:
            selected = choice(kana)
        before_c = selected
        if i == 6:
            f.write(selected + '(      ); \n')
            i = 0
        else:
            f.write(selected + '(      ); ')
            i += 1
    
    f.write('\n\n')
    before_d.clear()
    i = 0

    while len(romaji) > 0:
        selected = romaji[randint(0, len(romaji)-1)]
        before_d[selected] += 1
        if before_d[selected] == 10:
            romaji.remove(selected)
        while selected == before_c and len(romaji) > 1:
            selected = romaji[randint(0, len(romaji)-1)]
        before_c = selected
        if i == 6:
            f.write(selected + '(      ); \n')
            i = 0
        else:
            f.write(selected + '(      ); ')
            i += 1
