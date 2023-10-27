from pathlib import Path
import requests
from bs4 import BeautifulSoup as bs
import logging
from models import initialize_db
from utils import record_in_database
from extract import parse_document, ingest_data
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
        pdf_link = link.get("href")
        if record_in_database(url=pdf_link):
            print("in database")
            continue
        print(f"Fetching {pdf_link}")
        pdf_bytes = s.get(pdf_link, headers=headers, timeout=300, verify=False).content
        filename = pdf_link.split("/")[-1].replace("_Arrest_", "-")
        destination = Path.joinpath(root, "..", "logs", filename)
        destination.write_bytes(pdf_bytes)
        # save_record_to_db(url=pdf_link, filename=filename)
        data = parse_document(filename)
        ingest_data(filename=filename, data=data, url=pdf_link)

# def copy_db_to_docs():
#     """Copy DB to docs
#
#     This is a placeholder until i figure out what i want to structure this
#     Alot of this is set up to avoid openly displaying the data on github
#
#     :return:
#     """
#     original = Path.joinpath(root, "records.db")
#     destination = Path.joinpath(root, "..", "docs", "data", "records.db")
#     shutil.copyfile(original, destination)
#

def collect_records():
    """Collect records

    :return:
    """
    initialize_db()
    find_posted_records()


if __name__ == '__main__':
    """"""
    collect_records()
