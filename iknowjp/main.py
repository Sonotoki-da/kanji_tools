import asyncio
import json
from concurrent.futures import as_completed
import os
from typing import List

from requests import Response
from requests.exceptions import HTTPError, JSONDecodeError
from requests_futures.sessions import FuturesSession


def get_links() -> List[str]:
    return [
        # 1
        "https://iknow.jp/api/v2/goals/566921",
        "https://iknow.jp/api/v2/goals/566922",
        "https://iknow.jp/api/v2/goals/566924",
        "https://iknow.jp/api/v2/goals/566925",
        "https://iknow.jp/api/v2/goals/566926",
        "https://iknow.jp/api/v2/goals/566927",
        "https://iknow.jp/api/v2/goals/566928",
        "https://iknow.jp/api/v2/goals/566929",
        "https://iknow.jp/api/v2/goals/566930",
        "https://iknow.jp/api/v2/goals/566932",
        # 2
        "https://iknow.jp/api/v2/goals/594768",
        "https://iknow.jp/api/v2/goals/594770",
        "https://iknow.jp/api/v2/goals/594771",
        "https://iknow.jp/api/v2/goals/594772",
        "https://iknow.jp/api/v2/goals/594773",
        "https://iknow.jp/api/v2/goals/594774",
        "https://iknow.jp/api/v2/goals/594775",
        "https://iknow.jp/api/v2/goals/594777",
        "https://iknow.jp/api/v2/goals/594778",
        "https://iknow.jp/api/v2/goals/594780",
        # 3
        "https://iknow.jp/api/v2/goals/615865",
        "https://iknow.jp/api/v2/goals/615866",
        "https://iknow.jp/api/v2/goals/615867",
        "https://iknow.jp/api/v2/goals/615869",
        "https://iknow.jp/api/v2/goals/615871",
        "https://iknow.jp/api/v2/goals/615872",
        "https://iknow.jp/api/v2/goals/615873",
        "https://iknow.jp/api/v2/goals/615874",
        "https://iknow.jp/api/v2/goals/615876",
        "https://iknow.jp/api/v2/goals/615877",
        # 4
        "https://iknow.jp/api/v2/goals/615947",
        "https://iknow.jp/api/v2/goals/615949",
        "https://iknow.jp/api/v2/goals/615950",
        "https://iknow.jp/api/v2/goals/615951",
        "https://iknow.jp/api/v2/goals/615953",
        "https://iknow.jp/api/v2/goals/615954",
        "https://iknow.jp/api/v2/goals/615955",
        "https://iknow.jp/api/v2/goals/615957",
        "https://iknow.jp/api/v2/goals/615958",
        "https://iknow.jp/api/v2/goals/615959",
        # 5
        "https://iknow.jp/api/v2/goals/616077",
        "https://iknow.jp/api/v2/goals/616078",
        "https://iknow.jp/api/v2/goals/616079",
        "https://iknow.jp/api/v2/goals/616080",
        "https://iknow.jp/api/v2/goals/616081",
        "https://iknow.jp/api/v2/goals/616082",
        "https://iknow.jp/api/v2/goals/616083",
        "https://iknow.jp/api/v2/goals/616084",
        "https://iknow.jp/api/v2/goals/616085",
        "https://iknow.jp/api/v2/goals/616086",
        # 6
        "https://iknow.jp/api/v2/goals/598434",
        "https://iknow.jp/api/v2/goals/598432",
        "https://iknow.jp/api/v2/goals/598431",
        "https://iknow.jp/api/v2/goals/598430",
        "https://iknow.jp/api/v2/goals/598427",
        "https://iknow.jp/api/v2/goals/598426",
        "https://iknow.jp/api/v2/goals/598425",
        "https://iknow.jp/api/v2/goals/598424",
        "https://iknow.jp/api/v2/goals/598423",
        "https://iknow.jp/api/v2/goals/598422",
    ]


def _make_future_requests(links: List[str], session: FuturesSession):
    return as_completed([session.get(link) for link in links])  # type: ignore


def _make_json_dir() -> str:
    path = os.path.dirname(os.path.realpath(__file__)) + "/json/"
    try:
        os.makedirs(path)
    except:
        pass
    return path


async def fetch_and_save_jsons(links: List[str]) -> List[str]:
    filenames = []
    filepath = _make_json_dir()
    with FuturesSession() as session:
        for future in _make_future_requests(links, session):
            try:
                response: Response = future.result()
            except HTTPError as connection_error:
                print(f"A connection error: {connection_error}")
            except Exception as error:
                print(f"An error: {error}")
            else:
                try:
                    json_string = response.json()
                except JSONDecodeError as json_error:
                    print(f"A json error: {json_error}")
                else:
                    filename: str = filepath + json_string["title"] + ".json"
                    filename = filename.lower().replace(" ", "_").replace(":", "")
                    with open(filename, "w+") as f:
                        json.dump(json_string, f, ensure_ascii=False, indent=4)
                    print(
                        f"{response.url} have been downloaded and stored in the folder"
                        f" json with a name {filename}"
                    )
                    filenames.append(filename)
    return filenames


async def make_anki_cards(jsons: List[str]):
    for json_file in jsons:
        with open(json_file) as f:
            json.load(f)


async def main():
    await make_anki_cards(await fetch_and_save_jsons(get_links()))


if __name__ == "__main__":
    asyncio.run(main())
