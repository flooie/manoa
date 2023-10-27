from datetime import datetime

try:
    from models import Document, Arrest, Charge, Person
except ImportError:
    from .models import Document, Arrest, Charge, Person

from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc, event
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from pathlib import Path

Base = declarative_base()
root = Path(__file__).parent

def fetch_token(url: str):
    """"""
    if 'github' in url:
        key = "gh.txt"
    else:
        key = "local.txt"
    p = Path.joinpath(root, key)
    return p.read_text()


def connect_to_database(is_echoed: False):
    db_url = Path.joinpath(root, "..", "data", "manoa.db")
    engine = create_engine(f"sqlite:///{db_url}", echo=is_echoed)

    # Event listener for setting the date_created before inserting a new record
    @event.listens_for(Document, "before_insert")
    def set_date_created(mapper, connection, target):
        target.date_created = datetime.utcnow()

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def fetch_documents():
    s = connect_to_database(is_echoed=True)
    logs = s.query(Document).order_by(desc(Document.id)).all()
    s.close()
    return logs


def fetch_coordinates(doc_id=None):
    s = connect_to_database(is_echoed=True)
    if not doc_id:
        logs = s.query(Arrest).all()
    else:
        logs = s.query(Arrest).join(Charge).join(Person).join(Document).filter(Document.id == doc_id).all()
    s.close()
    return logs



def fetch_key():
    if Path("src/gh.txt").exists():
        with open("src/gh.txt", "r") as f:
            map_api = f.read()
        return map_api
    else:
        return "File not found"

def record_in_database(url):
    session = connect_to_database(is_echoed=False)
    filename = url.split("/")[-1].replace("_Arrest_", "-")
    q = session.query(Document).filter(Document.filename == filename)
    if q.count() > 0:
        return True
    return False

def parse_address(location):
    import requests
    map_api = fetch_key(url="")
    headers = {
        'Authorization': f'Bearer {map_api}',
    }
    response = requests.get('https://maps-api.apple.com/v1/token', headers=headers)
    token = response.json().get("accessToken", None)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        "https://maps-api.apple.com/v1/geocode",
        params={"q": location},
        headers=headers,
    )
    return response
