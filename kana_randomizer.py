"""
Kana generator for practicing it with the most efficient way.
Make a *.doc document from generated result and print it out.
"""

from random import choice
from collections import defaultdict


KANA = [
    "あ",
    "い",
    "う",
    "え",
    "お",
    "か",
    "き",
    "く",
    "け",
    "こ",
    "さ",
    "し",
    "す",
    "せ",
    "そ",
    "た",
    "ち",
    "つ",
    "て",
    "と",
    "な",
    "に",
    "ぬ",
    "ね",
    "の",
    "は",
    "ひ",
    "ふ",
    "へ",
    "ほ",
    "ま",
    "み",
    "む",
    "め",
    "も",
    "や",
    "ゆ",
    "よ",
    "ら",
    "り",
    "る",
    "れ",
    "ろ",
    "わ",
    "を",
    "ん",
    "ア",
    "イ",
    "ウ",
    "エ",
    "オ",
    "カ",
    "キ",
    "ク",
    "ケ",
    "コ",
    "サ",
    "シ",
    "ス",
    "セ",
    "ソ",
    "タ",
    "チ",
    "ツ",
    "テ",
    "ト",
    "ナ",
    "ニ",
    "ヌ",
    "ネ",
    "ノ",
    "ハ",
    "ヒ",
    "フ",
    "ヘ",
    "ホ",
    "マ",
    "ミ",
    "ム",
    "メ",
    "モ",
    "ヤ",
    "ユ",
    "ヨ",
    "ラ",
    "リ",
    "ル",
    "レ",
    "ロ",
    "ワ",
    "ヲ",
    "ン",
]
ROMAJI = [
    "a",
    "i",
    "u",
    "e",
    "o",
    "ka",
    "ki",
    "ku",
    "ke",
    "ko",
    "sa",
    "shi",
    "su",
    "se",
    "so",
    "ta",
    "chi",
    "tsu",
    "te",
    "to",
    "na",
    "ni",
    "nu",
    "ne",
    "no",
    "ha",
    "hi",
    "fu",
    "he",
    "ho",
    "ma",
    "mi",
    "mu",
    "me",
    "mo",
    "ya",
    "yu",
    "yo",
    "ra",
    "ri",
    "ru",
    "re",
    "ro",
    "wa",
    "wo",
    "n",
]
PARENTHTESIS = "(    ); "


def generate(mora_set: list[str], occurence: int = 4) -> str:
    # for counting how many times the same mora is selected
    mora_counter = defaultdict(int)
    selected_moras = []
    result = ""
    i = 0
    while len(selected_moras) != (len(mora_set) * occurence):
        selected_mora = choice(mora_set)

        if len(selected_moras) >= 2:
            if selected_mora == selected_moras[-1]:
                continue

        if mora_counter[selected_mora] == occurence:
            continue

        if selected_mora in ROMAJI:
            _ = len(selected_mora)
            if _ == 1:
                selected_mora += "  "
            elif _ == 2:
                selected_mora += " "

        if i == 6:
            result += selected_mora + PARENTHTESIS + "\n"
            i = 0
        else:
            result += selected_mora + PARENTHTESIS
            i += 1

        mora_counter[selected_mora.replace(" ", "")] += 1
        selected_moras.append(selected_mora)

    return result


if __name__ == "__main__":
    with open("kana practicing.txt", "w+", encoding="utf-8") as f:
        for x in [KANA, ROMAJI]:
            _ = generate(x)
            f.write(_)
            f.write("\n\n")
