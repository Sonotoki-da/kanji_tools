import requests
from bs4 import BeautifulSoup

from anki_tool import invoke

urls = [
    f"https://jlptsensei.com/jlpt-n4-kanji-list/",
    f"https://jlptsensei.com/jlpt-n4-kanji-list/page/2/",
    f"https://jlptsensei.com/jlpt-n3-kanji-list/",
    f"https://jlptsensei.com/jlpt-n3-kanji-list/page/2/",
    f"https://jlptsensei.com/jlpt-n3-kanji-list/page/3/",
    f"https://jlptsensei.com/jlpt-n3-kanji-list/page/4/",
    f"https://jlptsensei.com/jlpt-n2-kanji-list/",
    f"https://jlptsensei.com/jlpt-n2-kanji-list/page/2/",
    f"https://jlptsensei.com/jlpt-n2-kanji-list/page/3/",
    f"https://jlptsensei.com/jlpt-n2-kanji-list/page/4/",
    f"https://jlptsensei.com/jlpt-n1-kanji-list/"
]
for url in urls:
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    table = soup.find('table', id='jl-kanji')
    level = soup.title.text.split(' ')[1]
    invoke('createDeck', deck=f'JLPT Sensei N5-N1::JLPT Sensei {level} Kanji')
    notes = []
    for row in table.find_all('tr')[1:]:
        data = row.find_all('td')[1:]
        if not data:
            continue
        notes.append({
            'deckName': f'JLPT Sensei N5-N1::JLPT Sensei {level} Kanji',
            'modelName': 'japanese',
            'fields': {
                'Kanji': data[0].text,
                '読み方': f"{data[1].find('p').text}\n{data[2].find('p').text}",
                'ウズベク語での意味': data[3].text
            },
            'tags': [
                f'{level}', 'english', 'kanji'
            ]
        })

    print(invoke('addNotes', notes=notes))
