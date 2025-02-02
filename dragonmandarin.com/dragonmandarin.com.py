from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import re
from typing import Any
from urllib.parse import ParseResult, urljoin, urlparse, unquote
import argparse
from bs4 import BeautifulSoup
import requests


def _fetch_and_save_content(url: str, save_path: str):
    r = requests.get(url)
    r.raise_for_status()

    content = r.content.decode()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w+") as f:
        f.write(content)

    print(f"Downloaded html file and saved to {save_path}")

    return content


def _download_audio(url: str, save_path: str):
    try:
        with open(save_path) as _:
            print(f"Skipping; audio file exists: {save_path}")
            return save_path
    except FileNotFoundError:
        pass

    r = requests.get(url, stream=True)
    r.raise_for_status()

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb+") as audio_file:
        for chunk in r.iter_content(chunk_size=8192):
            audio_file.write(chunk)

    print(f"Downloaded audio file and saved to {save_path}")

    return save_path


def _add_audio_data(soup, url, data, save_path):
    if soup.audio:
        data |= {
            "audio_file": _download_audio(
                f"{url.scheme}://{url.hostname}{soup.audio.attrs["src"]}",
                os.path.join(
                    save_path,
                    f"audio/{unquote(soup.audio.attrs["src"]).split("/")[-1]}",
                ),
            )
        }
    else:
        data |= {"audio_file": None}


def _sort_and_save_json(listdata: list, filename):
    listdata = [x for x in listdata if x]
    listdata = sorted(listdata, key=lambda x: int(x["index"]))
    with open(filename.replace(".html", ".json"), "w+") as f:
        json.dump(listdata, f, ensure_ascii=False, indent=4)


def _start_threads(rows, url, refetch, save_path):
    listdata = []
    rows_len = len(rows)
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(_process_rows, row, url, refetch, save_path): i
            for i, row in enumerate(rows)
        }

        i = rows_len
        for future in as_completed(futures):
            print(f"Processed: {i} of {rows_len}")
            i -= 1
            listdata.append(future.result())

    return listdata


def _newlines_cleaned(i, columns):
    return " ".join(
        x.strip() for x in columns[i].get_text(strip=True).splitlines() if x.strip()
    )


def _fetch_and_soup(url: str, file_path: str, refetch=False) -> BeautifulSoup:
    if refetch:
        content = _fetch_and_save_content(url, file_path)
    else:
        try:
            with open(file_path) as f:
                content = f.read()
        except FileNotFoundError:
            content = _fetch_and_save_content(url, file_path)

    return BeautifulSoup(content, "html.parser")


def _process_rows(row, url: ParseResult, refetch: bool, save_path: str):
    data = {}
    if "characters" in url.path:
        columns = row.find_all("td")
        data = {
            "index": _newlines_cleaned(0, columns),
            "character": _newlines_cleaned(1, columns),
            "pinyin": _newlines_cleaned(2, columns),
            "definition": _newlines_cleaned(3, columns),
            "words": _newlines_cleaned(4, columns),
        }

        data |= {
            "detailed": _jsonify_individual_hanzi_page(
                urlparse(
                    urljoin(f"{url.scheme}://{url.netloc}", columns[1].a.attrs["href"])
                ),
                refetch,
                save_path,
            )
        }
    elif "words" in url.path:
        columns = row.find_all("td")
        data = {
            "index": _newlines_cleaned(0, columns),
            "character": _newlines_cleaned(1, columns),
            "pinyin": _newlines_cleaned(2, columns),
            "meaning": _newlines_cleaned(3, columns),
        }

        data |= {
            "detailed": _jsonify_individual_word_page(
                urlparse(
                    urljoin(f"{url.scheme}://{url.netloc}", columns[1].a.attrs["href"])
                ),
                refetch,
                save_path,
            )
        }
    return data


def _jsonify_individual_hanzi_page(
    url: ParseResult, refetch: bool, save_path: str
) -> dict[str, str]:
    data = {}
    soup: Any = _fetch_and_soup(
        url.geturl(),
        os.path.join(save_path, unquote(url.path.split("/")[-1]) + ".html"),
        refetch,
    )

    # Some pages don't have the definitions table, instead it's bulletins
    table = (
        soup.find(name="h2", string="DEFINITIONS")
        .find_parent("div")
        .find_next_sibling("div")
        .find("table")
    )
    if table:
        definitions = [x.get_text().strip().splitlines() for x in table.find_all("td")]
        definitions = [{x[0]: y} for x, y in zip(definitions[::2], definitions[1::2])]
    else:
        definitions = [
            x.get_text().strip()
            for x in soup.find(name="h2", string="DEFINITIONS")
            .find_parent("div")
            .find_next_sibling("ul")
            if x.get_text().strip()
        ]

    words = [
        [y.strip() for y in x.get_text().strip().splitlines() if y.strip()]
        for x in soup.find(name="h2", string="WORDS")
        .find_parent("div")
        .find_next_sibling("div")
        .find("table")
        .find_all("td")
    ]

    # At that time, there were 3 important tables: Character info, Definitions, Words
    data |= {
        "character_info": [
            dict([x.get_text().strip().replace("\n\n", "\n").splitlines()])
            if not x.find(string=re.compile("TRADITIONAL|SIMPLIFIED"))
            else {
                x.get_text().strip().replace("\n\n", "\n").splitlines()[0]: x.get_text()
                .strip()
                .replace("\n\n", "\n")
                .splitlines()[1:]
            }
            for x in soup.find(name="h2", string="Character")
            .find_next_sibling("table")
            .find_all("tr")
        ],
        "definitions": definitions,
        "words": [
            {" ".join(character[:2]): english}
            for character, english in zip(words[::2], words[1::2])
        ],
    }

    _add_audio_data(soup, url, data, save_path)

    return data


def _jsonify_individual_word_page(
    url: ParseResult, refetch: bool, save_path: str
) -> dict[str, str]:
    data = {}
    soup: Any = _fetch_and_soup(
        url.geturl(),
        os.path.join(save_path, unquote(url.path.split("/")[-1]) + ".html"),
        refetch,
    )

    definitions = soup.find(name="h2", string="DEFINITIONS").find_parent("div")
    if definitions.find_next_sibling("ul"):
        definitions = [
            x.get_text().strip()
            for x in definitions.find_next_sibling("ul")
            if x.get_text().strip()
        ]
    elif definitions.find_next_sibling("ol"):
        definitions = [
            x.get_text().strip()
            for x in definitions.find_next_sibling("ol")
            if x.get_text().strip()
        ]

    data |= {
        "word_info": [
            dict([x.get_text().strip().replace("\n\n", "\n").splitlines()])
            for x in soup.find(name="h2", string="Word")
            .find_next_sibling("table")
            .find_all("tr")
        ],
        "definitions": definitions,
    }

    _add_audio_data(soup, url, data, save_path)

    return data


def jsonify_characters_page(url: ParseResult, refetch: bool, save_path: str):
    filename = url.geturl().removeprefix("https://").replace("/", "_") + ".html"
    soup: Any = _fetch_and_soup(
        url.geturl(), os.path.join(save_path, filename), refetch
    )

    rows = soup.find("tbody").find_all("tr")
    listdata = _start_threads(rows, url, refetch, save_path)
    _sort_and_save_json(listdata, filename)


def jsonify_words_page(url: ParseResult, refetch: bool, save_path: str):
    filename = url.geturl().removeprefix("https://").replace("/", "_") + ".html"
    soup: Any = _fetch_and_soup(
        url.geturl(), os.path.join(save_path, filename), refetch
    )

    rows = [
        x
        for x in soup.find("tbody").find_all("tr")
        if x.find("a", attrs={"href": lambda x: "words" in x})
    ]
    listdata = _start_threads(rows, url, refetch, save_path)
    _sort_and_save_json(listdata, filename)


def main(args):
    if "characters" in args.url:
        jsonify_words_page(urlparse(args.url), args.refetch, args.output)
    elif "words" in args.url.find("words"):
        jsonify_characters_page(urlparse(args.url), args.refetch, args.output)
    else:
        print("Incorrect URL")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch HSK characters and words from dragonmandarin.com"
    )
    parser.add_argument(
        "url",
        type=str,
        help="""Strict URLs to fetch HSK characters or words from dragonmandarin.com
        Example: python dragonmandarin.com.py https://dragonmandarin.com/hsk1/characters""",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="./data",
        help='Output directory of html and audio files, JSON files will always be in "./" (default: current directory "./data")',
    )
    parser.add_argument(
        "-f",
        "--refetch",
        action="store_true",
        help="Force refetch fresh files. (default: False)",
    )
    args = parser.parse_args()

    main(args)
