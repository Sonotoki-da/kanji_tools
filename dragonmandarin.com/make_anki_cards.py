import json
import genanki
from random import randint
from glob import glob


def generate_id():
    return randint(0, 99999999)


hsk_package = genanki.Package(
    [genanki.Deck(generate_id(), f"HSK 1-6 Hanzi::HSK {i} Hanzi") for i in range(6)]
)

hanzi = genanki.Model(
    generate_id(),
    "hanzi",
    fields=[
        {"name": "Character"},
        {"name": "Pinyin"},
        {"name": "Definitions"},
        {"name": "Words"},
        {"name": "Audio"},
    ],
    templates=[
        {
            "name": "Hanzi",
            "qfmt": "<p style='text-align: center;'><b>汉字</b></p><br><h1>{{Character}}</h1>",
            "afmt": """
                {{FrontSide}}
                <hr>
                <p style="text-align: center;"><b>Pinyin</b></p><h2>{{Pinyin}}</h2>
                <hr>
                <p><strong class="centered">Definitions:</strong><br>{{Definitions}}</p>
                <hr>
                <p><strong class="centered">Words:</strong><br>{{Words}}</p>
                """,
        },
    ],
    css="""
    body {
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
    .centered {
        margin: 0 200px;
    }
    .hanzi-colored {
        display: inline;
        color: #E74C3C;
    }
    .pinyin-colored {
        display: inline;
        color: #1ABC9C;
    }
    """,
)

for deck in hsk_package.decks:  # type: ignore
    deck.add_model(hanzi)

jsons = []
for x in glob("./*json"):
    with open(x) as f:
        jsons.append(json.load(f))


def process_deck(data, deck):
    for x in data:
        character = x["character"]
        pinyin = x["pinyin"]

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
                definitions += d

        definitions = "<div class='centered'>" + definitions + "</div>"
        words = "<br>".join(
            f"<div class='centered'><div class='hanzi-colored'>{word.split(' ')[0]} </div><div class='pinyin-colored'>{' '.join(word.split(' ')[1:])}</div>: {' '.join(defs)}</div>"
            for word_dict in x["detailed"]["words"]
            for word, defs in word_dict.items()
        )
        audio_file = (
            x["detailed"]["audio_file"].split("/")[-1]
            if x["detailed"]["audio_file"]
            else ""
        )

        note = genanki.Note(
            model=hanzi,
            fields=[
                character,
                pinyin + f" [sound:{audio_file}]",
                definitions,
                words,
                audio_file,
            ],
        )
        deck.add_note(note)


audio_files = []
for i, x in enumerate(jsons):
    audio_files += [
        y["detailed"]["audio_file"] for y in x if y["detailed"]["audio_file"]
    ]
    process_deck(x, hsk_package.decks[i])  # type: ignore

hsk_package.media_files = audio_files
hsk_package.write_to_file("hsk_1_6_hanzi.apkg")

print("Anki package created successfully!")
