import json
import argparse
from bs4 import BeautifulSoup
import requests


def main(url: str):
    filename = url.removeprefix("https://").replace("/", "_") + ".html"
    try:
        with open(filename) as f:
            content = f.read()
    except FileNotFoundError:
        r = requests.get(url)
        if r.status_code == 200:
            content = r.content.decode()
            with open(filename, "w+") as f:
                f.write(content)
        else:
            raise requests.HTTPError

    soup = BeautifulSoup(content, "html.parser")
    rows = soup.find_all("tr")
    data = []

    def newlines_cleaned(i, columns):
        return " ".join(
            x.strip() for x in columns[i].get_text(strip=True).splitlines() if x.strip()
        )

    for row in rows:
        columns = row.find_all("td")
        if not columns:
            continue

        row_data = {
            "index": newlines_cleaned(0, columns),
            "character": newlines_cleaned(1, columns),
            "pinyin": newlines_cleaned(2, columns),
            "definition": newlines_cleaned(3, columns),
            "words": newlines_cleaned(4, columns),
        }
        data.append(row_data)

    with open(filename.replace(".html", ".json"), "w+") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


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
    args = parser.parse_args()

    try:
        main(args.url)
    except Exception:
        print("You're probably on the wrong website")
