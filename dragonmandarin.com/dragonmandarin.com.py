import json
import os
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
    r = requests.get(url, stream=True)
    r.raise_for_status()

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb+") as audio_file:
        for chunk in r.iter_content(chunk_size=8192):
            audio_file.write(chunk)

    print(f"Downloaded audio file and saved to {save_path}")

    return save_path


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


def jsonify_main_page(url: ParseResult, refetch: bool, save_path: str):
    filename = url.geturl().removeprefix("https://").replace("/", "_") + ".html"
    soup = _fetch_and_soup(url.geturl(), os.path.join(save_path, filename), refetch)
    listdata = []
    data = {}

    trs = soup.find_all("tr")
    trs_len = len(trs)
    for i, row in enumerate(trs):
        columns = row.find_all("td")
        if not columns:
            continue

        print(f"Progress: {i} of {trs_len}")

        data = {
            "index": _newlines_cleaned(0, columns),
            "character": _newlines_cleaned(1, columns),
            "pinyin": _newlines_cleaned(2, columns),
            "definition": _newlines_cleaned(3, columns),
            "words": _newlines_cleaned(4, columns),
        }

        data |= {
            "detailed": jsonify_hanzi_page(
                urlparse(
                    urljoin(f"{url.scheme}://{url.netloc}", columns[1].a.attrs["href"])
                ),
                refetch,
                save_path,
            )
        }
        listdata.append(data)

    with open(filename.replace(".html", ".json"), "w+") as f:
        json.dump(listdata, f, ensure_ascii=False, indent=4)


def jsonify_hanzi_page(
    url: ParseResult, refetch: bool, save_path: str
) -> dict[str, str]:
    data = {}
    soup = _fetch_and_soup(
        url.geturl(),
        os.path.join(save_path, unquote(url.path.split("/")[-1]) + ".html"),
        refetch,
    )

    # At that time, there were 3 important tables: Character info, Definitions, Words
    tables = soup.find_all("table")
    definitions = [x.get_text().strip().splitlines() for x in tables[1].find_all("td")]
    words = [
        [y.strip() for y in x.get_text().strip().splitlines() if y.strip()]
        for x in tables[2].find_all("td")
    ]
    data |= {
        "character_info": [
            dict([x.get_text().strip().splitlines()]) for x in tables[0].find_all("tr")
        ],
        "definitions": [{x[0]: y} for x, y in zip(definitions[::2], definitions[1::2])],
        "words": [
            {" ".join(character[:2]): english}
            for character, english in zip(words[::2], words[1::2])
        ],
    }

    data |= {
        "audio_file": _download_audio(
            f"{url.scheme}://{url.hostname}{soup.audio.attrs["src"]}",  # type: ignore
            os.path.join(
                save_path,
                f"./audio/{unquote(soup.audio.attrs["src"]).split("/")[-1]}",  # type: ignore
            ),
        )
    }

    return data


def main(args):
    jsonify_main_page(urlparse(args.url), args.refetch, args.output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch HSK characters from dragonmandarin.com"
    )
    parser.add_argument(
        "url",
        type=str,
        help="""The URL to fetch HSK characters from.
        Example: python dragonmandarin.com.py https://dragonmandarin.com/hsk1/characters""",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="./data",
        help='Output directory (default: current directory "./data")',
    )
    parser.add_argument(
        "-f",
        "--refetch",
        action="store_true",
        help="Force refetch a fresh page. (default: False)",
    )
    args = parser.parse_args()

    try:
        main(args)
    except Exception as e:
        print(f"An error occurred: {e}")
        print("You're probably on the wrong website")
