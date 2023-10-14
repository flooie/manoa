import argparse
from pathlib import Path

import requests
from bs4 import BeautifulSoup as bs
import logging

from models import initialize_db, record_in_database, save_record_to_db

root = Path(__file__).parent

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Host': 'www.honolulupd.org',
    'User-Agent': 'flooie',
    'Accept-Language': 'en-US,en;q=0.9',
    'Sec-Fetch-Dest': 'document',
    'Connection': 'keep-alive',
}

def find_posted_records():
    """"""
    url = "https://www.honolulupd.org/information/arrest-logs/"
    s = requests.session()
    website = s.get(url, headers=headers, timeout=30, verify=False)
    if website.status_code != 200:
        logging.warning(f"Website status code: {website.status_code}")
        return
    soup = bs(website.content, features="lxml")
    for link in soup.find_all('a', href=lambda href: href and 'pdf' in href and "arrest-logs" in href):
        print(link.get("href"))
        pdf_link = link.get("href")

        if record_in_database(url=pdf_link):
            print("RECORD IN DATABASE?")
            continue
        pdf_bytes = s.get(pdf_link, headers=headers, timeout=300, verify=False).content
        filename = pdf_link.split("/")[-1]
        destination = Path.joinpath(root, "files", filename)
        destination.write_bytes(pdf_bytes)
        print("Record", destination)
        save_record_to_db(url=pdf_link, filename=filename)


def collect_records():
    """

    :return:
    """
    initialize_db()
    find_posted_records()


if __name__ == '__main__':

    collect_records()
