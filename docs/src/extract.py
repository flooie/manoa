from urllib.parse import urlparse

import pdfplumber
import requests
from pdf2image import convert_from_path
from pathlib import Path
import pytesseract
from tempfile import NamedTemporaryFile
import os
from dotenv import load_dotenv
import time
from models import Document, Person, Charge, Officer, Arrest, initialize_db
from models import connect_to_database
from utils import fetch_token
load_dotenv()
root = Path(__file__).parent

MAP_TOKEN = os.getenv("MAP_TOKEN")

def top_bottom(obj):
    if obj["doctop"] < 2436 and "/":
        return True


def make_person(line, page):
    """

    :param line:
    :param page:
    :return:
    """
    left, top, right, bottom = (300, line["top"], 580, line["top"] + 50)
    race_box = (left, top, right, bottom)
    left, top, right, bottom = (580, line["top"], 2000, line["top"] + 50)
    name_bbox = (left, top, right, bottom)
    left, top, right, bottom = (line["x0"], line["top"] + 50, 300, line["top"] + 100)
    time_bbox = (left, top, right, bottom)
    left, top, right, bottom = (300, line["top"] + 50, 580, line["top"] + 100)
    age_sex_bbox = (left, top, right, bottom)

    race = page.crop(bbox=race_box).extract_text()
    name = page.crop(bbox=name_bbox).extract_text()
    time = page.crop(bbox=time_bbox).extract_text()
    age_sex = page.crop(bbox=age_sex_bbox).extract_text()
    cd = {
        "name": name.strip(),
        "race": race.strip(),
        "date": line["text"].strip(),
        "time": time.strip(),
        "sex": age_sex.split("/")[0].strip(),
        "age": age_sex.split("/")[1].strip(),
    }
    return cd


def make_charge(line, page):
    if line["text"] == "Offense":
        return

    name_bbox = (1250, line["doctop"], 1800, line["doctop"] + 50)
    name = page.crop(bbox=name_bbox).extract_text()

    statute_bbox = (1250, name_bbox[1] + 50, 1800, name_bbox[3] + 100)
    statute = page.crop(bbox=statute_bbox).extract_text()

    location_bbox = (1800, line["doctop"], 2600, line["doctop"] + 50)
    location = page.crop(bbox=location_bbox).extract_text()

    officer_bbox = (1800, line["doctop"] + 50, 2600, line["doctop"] + 100)
    officer = page.crop(bbox=officer_bbox).extract_text()

    court_bbox = (1800, line["doctop"] + 100, 2600, line["doctop"] + 150)
    court = page.crop(bbox=court_bbox).extract_text()

    rel_datetime__bbox = (2600, line["doctop"], page.width, line["doctop"] + 50)
    rel_datetime = page.crop(bbox=rel_datetime__bbox).extract_text()

    released_bbox = (2600, line["doctop"] + 50, page.width, line["doctop"] + 100)
    how_released = page.crop(bbox=released_bbox).extract_text()

    charge = {
        "charge": line["text"].strip(),
        "crime": name.split("\n")[0].strip(),
        "statute": statute.strip(),
        "how_released": how_released.strip(),
        "rel_datetime": rel_datetime.split("\n")[0].strip(),
        "court": court.strip(),
        "officer": officer.strip(),
        "location": location.split("\n")[0].strip(),
    }
    return charge


def parse_document(filename):

    filepath = Path.joinpath(root, "..", "logs", filename)
    pages = convert_from_path(filepath, 300)
    charges = []
    people = []
    person_object = None
    charge_list = []
    for i, page in enumerate(pages):
        data = pytesseract.image_to_pdf_or_hocr(page, config="hocr")
        with NamedTemporaryFile() as f:
            f.write(data)
            # people, charges = process_pdf_from_date(f, people, charges)

            with pdfplumber.open(f.name) as pdf:
                first_page = pdf.pages[0]
                for line in first_page.filter(top_bottom).extract_words():
                    # print(line)
                    if round(line["x0"]) == 972:
                        if line["text"] == "Offense":
                            continue
                        charge = make_charge(line, first_page)
                        charge_list.append(charge)
                        continue
                    elif (
                        "/" not in line["text"]
                        or not len(line["text"]) == 10
                        or line["x0"] > 90
                    ):
                        continue

                    if person_object:
                        person_object["charges"] = charge_list
                        people.append(person_object)
                        charge_list = []
                        person_object = None

                    person_object = make_person(line, first_page)

    # Add last person object and charges
    person_object["charges"] = charge_list
    people.append(person_object)

    # import pprint
    # pprint.pprint(people)
    return people


def ingest_data(filename, data):

    session = connect_to_database(is_echoed=False)

    # Create a document instance
    document = Document(filename=filename)
    q = session.query(Document).filter(Document.filename == filename)
    if q.count() > 0:
        # results = session.query(Document).all()
        # for result in results:
        #     session.delete(result)
        # results = session.query(Person).all()
        # for result in results:
        #     session.delete(result)
        # results = session.query(Arrest).all()
        # for result in results:
        #     session.delete(result)
        # results = session.query(Officer).all()
        # for result in results:
        #     session.delete(result)
        # results = session.query(Charge).all()
        # for result in results:
        #     session.delete(result)
        #
        # session.commit()
        # session.close()
        # print("start over ")
        return

    session.add(document)
    session.commit()
    for person_data in data:
        person = Person(
            name=person_data["name"],
            race=person_data["race"],
            sex=person_data["sex"],
            age=person_data["age"],
            document_id=document.id,
        )
        session.add(person)
        session.commit()
        if len(person_data["charges"]) == 0:
            document.pdf_processed = False

            continue
        # Create an officer instance
        officer_data = person_data["charges"][0]["officer"]
        officer = Officer(name=officer_data)
        session.add(officer)
        session.commit()

        # Create charge instances and link them to the person and officer
        for charge_data in person_data["charges"]:

            q = session.query(Arrest).filter(Arrest.location == charge_data['location'])
            if q.count() == 1:
                coordinates = {
                    "latitude": q[0].latitude,
                    "longitude": q[0].longitude
                }
            else:
                coordinates = find_location(charge_data['location'])

            if coordinates:
                arrest = Arrest(
                    date=person_data["date"],
                    time=person_data["time"],
                    location=charge_data["location"],
                    latitude=coordinates['latitude'],
                    longitude=coordinates['longitude']
                )
            else:
                arrest = Arrest(
                    date=person_data["date"],
                    time=person_data["time"],
                    location=charge_data["location"],
                    longitude=0,
                    latitude=0

                )

            session.add(arrest)
            session.commit()

            charge = Charge(
                charge=charge_data["charge"],
                court=charge_data["court"],
                crime=charge_data["crime"],
                how_released=charge_data["how_released"],
                rel_datetime=charge_data["rel_datetime"],
                statute=charge_data["statute"],
                person_id=person.id,
                officer_id=officer.id,
                arrest_id=arrest.id
            )

            session.add(charge)
            session.commit()

    document.pdf_processed = True
    session.commit()
    session.close()

def find_location(location):
    loc = f"{location}, Oahu, HI"
    # print(location)
    response = parse_address(loc)
    if response.status_code != 200:
        # print("FAILED")
        # print(response.status_code)
        # print(response.content)
        return {}
    address = response.json()
    if len(address["results"]) == 0:
        print("NONE FOUND")
        return {}
    # print("FOUND IT HERE AND ADD IT")
    # print(address["results"][0]["coordinate"])
    return address["results"][0]["coordinate"]


def query_locations():
    """This method can be used for clean up

    A separate method can be called while parsing the documents to
    extract out the location information.  this will let us keep it up to
    date with mapping locations and in a nice way not over use the tool


    :return:
    """

    s = connect_to_database(is_echoed=False)
    unique_locations = s.query(Charge.location).group_by(Charge.location).all()
    for location in unique_locations:
        if len(location[0]) < 4:
            continue
        loc = f"{location[0]}, Oahu, HI"
        response = parse_address(loc)
        if response.status_code != 200:
            break
        address = response.json()
        # print(address)
        if len(address["results"]) == 0:
            print(loc)
        time.sleep(2)
        break


def parse_address(location):
    """This runs on the server"""
    w = urlparse(str("https://flooie.github.io/manoa"))
    map_api = fetch_token(w)
    headers = {
        'Authorization': f'Bearer {map_api}',
    }
    response = requests.get('https://maps-api.apple.com/v1/token', headers=headers)
    token = response.json().get("accessToken", None)
    # print(token, response.json(), response.status_code, map_api)
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        "https://maps-api.apple.com/v1/geocode",
        params={"q": location},
        headers=headers,
    )
    # print(response.json())
    return response



# if __name__ == "__main__":
#     """"""
#     parse_address("76 Reservoir street cambridge, ma")
    # initialize_db()
    # import glob
    # glob_path = Path.joinpath(root, "..", "logs", "*")
    # for filepath in glob.glob(str(glob_path)):
    #     print(filepath)
    #     fn = filepath.split("/")[-1]
    #     data = parse_document(fn)
    #     ingest_data(filename=fn, data=data)

    # parse_address("76 Reseroir street, cambridge ma ")