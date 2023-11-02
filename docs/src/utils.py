from datetime import datetime

try:
    from models import Document, Arrest, Charge, Person, Officer
except ImportError:
    try:
        from .models import Document, Arrest, Charge, Person, Officer
    except ImportError:
        from src.models import Document, Arrest, Charge, Person, Officer

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
    from sqlalchemy import create_engine, func
    from sqlalchemy.orm import sessionmaker, joinedload
    s = connect_to_database(is_echoed=True)
    
    if not doc_id or doc_id == "Select log":
        logs = s.query(Arrest).options(joinedload(Arrest.charges)).all()
    else:
        logs = s.query(Arrest).join(Charge).join(Person).join(Document).filter(Document.id == doc_id).options(joinedload(Arrest.charges)).all()
    s.close()
    return logs

# def fetch_charges(charge_id=None):
#     s = connect_to_database(is_echoed=True)
#     charges = s.query(Charge).all()
#     s.close()
#     


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

def get_data(charge_id=1):
    session = connect_to_database(is_echoed=False)
    charge = session.query(Charge).filter(Charge.id==charge_id)

    # Call the as_dict method
    charge_data = charge[0].as_dict()
    return charge_data

def get_person(person_id: int):
    session = connect_to_database(is_echoed=False)
    person = session.query(Person).filter(Person.id==person_id)
    return person


def get_people():
    s = connect_to_database(is_echoed=False)
    unique_people = s.query(Person.name).group_by(Person.name).all()
    return unique_people

def get_officers(filter=None):
    s = connect_to_database(is_echoed=False)
    if filter==None:
        officers = s.query(Officer.name).group_by(Officer.name).all()
    else:
        officers = s.query(Officer).filter(Officer.name==filter).all()
    return officers

def get_crimes(filter=None):
    s = connect_to_database(is_echoed=False)
    if filter==None:
        crimes = s.query(Charge.crime).group_by(Charge.crime).all()
    else:
        crimes = s.query(Charge).filter(Charge.crime==filter).all()
    return crimes

