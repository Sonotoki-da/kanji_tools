# お好みのアニメシリーズから漢字全てを自動的に引取るために作られたスクリプトです。
# 勉強にもお役に立てると思いながらこういうツアーを書き始めたのです。
# (c)ソノトキ；２０２１年９月
# 前提モジュールは：pip install pysubs2

import pysubs2
from os import chdir
from glob import glob
import re

ALL_KANJI = re.compile('([一-龯])')
output_name = '「無能なナナ」から取られた漢字全て.txt'

chdir('c:/users/user/downloads')
with open(output_name, 'w+', encoding='utf-8') as f:
    all_kanji = set()
    for ass in glob('**/*.ass', recursive=True):
        assf = pysubs2.load(ass)
        f.write(ass + ':\n')
        for id, event in enumerate(assf.events):
            kanji = set(ALL_KANJI.findall(event.text))
            if kanji:
                all_kanji.update(kanji)
                f.write(f'{id}: ' + ''.join(kanji) + '\n')
        f.write('\n\n')
    f.write(f'\nAll kanji:\n{"".join(all_kanji)}')
