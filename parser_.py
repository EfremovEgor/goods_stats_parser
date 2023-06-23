from bs4 import BeautifulSoup
import re
import csv
import datetime


def chunk_split(lst: list, chunk_size: int) -> list:
    chunked_list = list()
    for i in range(0, len(lst), chunk_size):
        chunked_list.append(lst[i : i + chunk_size])
    return chunked_list


def parse_search_results(
    part_number: str, market_place_id: str, market: str, html: str
) -> None:
    html_objects = BeautifulSoup(html, "lxml")
    table = html_objects.find(
        "a", attrs={"href": f"/wb/keywords/{market_place_id}"}
    ).parent.parent.parent
    objs = table.find_all(string=re.compile("\d\d\.\d\d"))
    dates = [obj.text.strip() for obj in objs]
    srchs = table.find_all("svg", attrs={"class": "bi-search"})
    vals = table.find_all(attrs={"col-id": re.compile("\d\d_\d\d")})
    vals = chunk_split(vals, 15)
    payload = list()
    for _, (lst, srch) in enumerate(zip(vals[3:], srchs)):
        words = srch.parent.parent.find(
            "a", {"title": re.compile("Информация по ключевому слову")}
        ).text
        frequency = list(srch.parent.parent.parent.parent.parent.children)[
            1
        ].text.strip()
        frequency = frequency if frequency != "—" else "0"
        positions = [
            val.text.strip() if val.text.strip() != "—" else None for val in lst
        ]
        payload.append([words, frequency, positions])
    payload.sort(key=lambda x: int(x[1].replace(" ", "")), reverse=True)
    with open("./data/associated_words_avg.csv", "a", newline="") as f:
        writer = csv.writer(f)
        for val in payload[:5]:
            for i, position in enumerate(val[2]):
                if position is None:
                    position = "0"
                writer.writerow(
                    [
                        part_number,
                        market_place_id,
                        market,
                        val[0],
                        datetime.datetime.strptime(f"{dates[i]}.2023", "%d.%m.%Y"),
                        position,
                    ]
                )


def parse_all(part_number: str, market_place_id: str, market: str, html: str) -> None:
    parse_search_results(part_number, market_place_id, market, html)
    parse_average(part_number, market_place_id, market, html)


def parse_average(
    part_number: str, market_place_id: str, market: str, html: str
) -> None:
    html_objects = BeautifulSoup(html, "lxml")
    table = html_objects.find(
        "a", attrs={"href": f"/wb/keywords/{market_place_id}"}
    ).parent.parent.parent
    counter = 0
    objs = table.find_all(string=re.compile("\d\d\.\d\d"))
    dates = [obj.text.strip() for obj in objs]
    objs = table.find_all(attrs={"col-id": re.compile("\d\d_\d\d")})
    with open("./data/average.csv", "a", newline="") as f:
        writer = csv.writer(f)
        for obj in objs[len(dates) + 1 :]:
            counter += 1
            if counter in range(len(dates), len(dates) * 2 + 1):
                date = dates[counter % len(dates)]
                position = obj.text.strip()
                if position == "—":
                    position = None
                row = [
                    part_number,
                    market_place_id,
                    market,
                    datetime.datetime.strptime(f"{date}.2023", "%d.%m.%Y"),
                    position,
                ]
                if position:
                    writer.writerow(row)
