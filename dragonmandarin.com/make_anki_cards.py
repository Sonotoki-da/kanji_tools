from collections import defaultdict
import json
import genanki
from random import randint
from glob import glob


def generate_id():
    return randint(0, 99999999)


hsk_package = genanki.Package(
    [genanki.Deck(generate_id(), f"HSK 1-6 Decks::HSK {i}::Words") for i in range(1, 7)]
    + [
        genanki.Deck(generate_id(), f"HSK 1-6 Decks::HSK {i}::Hanzi")
        for i in range(1, 7)
    ]
)


css = """
body {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 0;
    font-size: 1.2em;
}
h1 {
    margin: 0;
    text-align: center;
    font-size: 4em;
    color: #E74C3C;  /* Bright color for character */
}
h2 {
    margin: 0;
    text-align: center;
    font-size: 2em;
    color: #1ABC9C;  /* Teal color for pinyin */
}
p {
    margin: 0;
    text-align: left;
    color: #ECF0F1;  /* Light text color for paragraphs */
}
.hanzi-colored {
    display: inline;
    color: #E74C3C;
}
.pinyin-colored {
    display: inline;
    color: #1ABC9C;
}
.centered-list {
    list-style-type: disc;
    padding-left: 20px; /* Indentation */
}

.centered-list li {
    margin: 5px 0;
}
"""

hanzi_model = genanki.Model(
    generate_id(),
    "hsk_hanzi",
    fields=[
        {"name": "Character"},
        {"name": "Pinyin"},
        {"name": "Definitions"},
        {"name": "Words"},
        {"name": "Audio"},
    ],
    templates=[
        {
            "name": "HSK_Hanzi",
            "qfmt": "<p style='text-align: center;'><b>汉字</b></p><br><h1>{{Character}}</h1>",
            "afmt": """
                {{FrontSide}}
                <hr>
                <p style="text-align: center;"><b>Pinyin</b></p><h2>{{Pinyin}}</h2>
                <hr>
                <p><strong style="text-align: center;">Definitions:</strong><br>{{Definitions}}</p>
                <hr>
                <p><strong style="text-align: center;">Words:</strong><br>{{Words}}</p>
                """,
        },
    ],
    css=css,
)
words_model = genanki.Model(
    generate_id(),
    "hsk_words",
    fields=[
        {"name": "Character"},
        {"name": "Pinyin"},
        {"name": "Meaning"},
        {"name": "Audio"},
    ],
    templates=[
        {
            "name": "HSK_Words",
            "qfmt": "<p style='text-align: center;'><b>汉字</b></p><br><h1>{{Character}}</h1>",
            "afmt": """
                {{FrontSide}}
                <hr>
                <p style="text-align: center;"><b>Pinyin</b></p><h2>{{Pinyin}}</h2>
                <hr>
                <p><strong style="text-align: center;">Meanings:</strong><br>{{Meaning}}</p>
                """,
        },
    ],
    css=css,
)


def process_deck(data, deck, is_hanzi: bool):
    fields = []
    for x in data:
        character = x["character"]
        pinyin = x["pinyin"]
        audio_file = (
            x["detailed"]["audio_file"].split("/")[-1]
            if x["detailed"]["audio_file"]
            else ""
        )

        definitions = ""
        for d in x["detailed"]["definitions"]:
            if type(d) is dict:
                definitions += (
                    "".join(
                        [
                            f"<div class='hanzi-colored'>{k.split(' ')[0]} </div><div class='pinyin-colored'>{k.split(' ')[1]}</div>: {", ".join(v)}"
                            for k, v in d.items()
                        ]
                    )
                    + "<br>"
                )
            else:
                definitions += f"<li>{d}</li>"

        if "<li>" in definitions:
            definitions = f"<ul class='centered-list'>{definitions}</ul>"
        else:
            definitions = f"{definitions}"
        fields += [
            character,
            pinyin + f" [sound:{audio_file}]",
            definitions,
        ]
        if is_hanzi:
            words = "<br>".join(
                f"<div class='centered'><div class='hanzi-colored'>{word.split(' ')[0]} </div><div class='pinyin-colored'>{' '.join(word.split(' ')[1:])}</div>: {' '.join(defs)}</div>"
                for word_dict in x["detailed"]["words"]
                for word, defs in word_dict.items()
            )
            fields.append(words)

        note = genanki.Note(
            model=hanzi_model if is_hanzi else words_model, fields=fields + [audio_file]
        )
        deck.add_note(note)
        fields = []


for i, deck in enumerate(hsk_package.decks):  # type: ignore
    if i > 6:
        deck.add_model(hanzi_model)
    else:
        deck.add_model(words_model)

jsons = defaultdict(list)
for x in glob("./*json"):
    with open(x) as f:
        if "words" in x:
            jsons["words"] += [json.load(f)]
        else:
            jsons["hanzi"] += [json.load(f)]


audio_files = []
i = 0
for x in jsons:
    for y in jsons[x]:
        audio_files += [
            z["detailed"]["audio_file"] for z in y if z["detailed"]["audio_file"]
        ]
        process_deck(y, hsk_package.decks[i], True if x == "hanzi" else False)  # type: ignore
        i += 1

hsk_package.media_files = audio_files
hsk_package.write_to_file("hsk1-6_words_hanzi.apkg")

print("Anki packages created successfully!")
