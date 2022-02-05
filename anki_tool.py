import json
import urllib.request
import time

start_time = time.time()

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}


def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(
        urllib.request.Request('http://localhost:8765', requestJson)))
    try:
        if len(response) != 2:
            raise Exception('response has an unexpected number of fields')
        if 'error' not in response:
            raise Exception('response is missing required error field')
        if 'result' not in response:
            raise Exception('response is missing required result field')
        if response['error'] is not None:
            raise Exception(response['error'])
    except:
        pass
    return response['result']


with open('kanji-jouyou.json', encoding='utf-8') as f:
    jouyou: dict = json.load(f)
jouyou
notes = []
jlpt_new = []
jlpt_old = []
not_jlpt = []
for x in jouyou:
    if jouyou[x]['jlpt_new'] is None:
        jlpt_new.append(x)
    if jouyou[x]['jlpt_old'] is None:
        jlpt_old.append(x)
    if jouyou[x]['jlpt_old'] is None and jouyou[x]['jlpt_new'] is None:
        not_jlpt.append(x)
    level = 'N' + str(jouyou[x]['jlpt_new'])
    notes.append({
        'deckName': f'常用漢字|JLPT再編成::{level}',
        'modelName': 'japanese_en',
        'fields': {
                    'Kanji': x,
                    '音読み': ', '.join(jouyou[x]['readings_on']),
                    '訓読み': ', '.join(jouyou[x]['readings_kun']),
                    '意味': ', '.join(jouyou[x]['meanings'])
        },
        'tags': [
            level, 'kanji', f"strokes: {jouyou[x]['strokes']}", 
        ]
    })

print("--- %s seconds ---" % (time.time() - start_time))