from datetime import datetime
from .models import Document, Arrest, Charge, Person
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc, event
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from pathlib import Path

Base = declarative_base()
root = Path(__file__).parent
print(root)

def fetch_token(url: str):
    filename = "local" if "localhost" in url.netloc else "gh"
    with open(f"src/{filename}.txt", "r") as f:
        return f.read()

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


# def save_record_to_db(url, filename):
#     """"""
#     # fn = filepath.split("/")[-1]
#     data = parse_document(filename)
#     ingest_data(filename=filename, data=data)

    # fn = filename
    # data = parse_document(fn)
    # ingest_data(filename=fn, data=data)
    #
    # s = connect_to_database(is_echoed=True)
    # new_log = Document(**{"url": url, "filename": filename})
    # s.add(new_log)


def fetch_key():
    if Path("src/local.txt").exists():
        with open("src/local.txt", "r") as f:
            map_api = f.read()
        return map_api
    else:
        return "File not found"

def record_in_database(url):
    session = connect_to_database(is_echoed=False)
    q = session.query(Document).filter(Document.url == url)
    if q.count() > 0:
        return True
    return False

def parse_address(location):
    # needed = True
    # if needed:
    import requests
    # MAP_API = os.getenv("MAP_API")
    map_api = fetch_key()
    headers = {
        'Authorization': f'Bearer {map_api}',
    }
    response = requests.get('https://maps-api.apple.com/v1/token', headers=headers)
    # token = response.json()['accessToken']
    # print(token)
    # # else:
    # #     token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJtYXBzYXBpIiwidGlkIjoiTEVDVlJQTVFUSyIsImFwcGlkIjoiTEVDVlJQTVFUSy5tYXBzLmZsb29pZS5jb20iLCJpdGkiOmZhbHNlLCJpcnQiOmZhbHNlLCJpYXQiOjE2OTc3Mzk3MDUsImV4cCI6MTY5Nzc0MTUwNX0.IrvsBr4uxTjj8wS8KPnQ0OMw_8Bh5hqzHRweoBs_Sv2mUW1XjpJitsyN1q900XSU6WkVn51LMSO-wn6E6rPSjQ"
    # #     # token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJtYXBzYXBpIiwidGlkIjoiTEVDVlJQTVFUSyIsImFwcGlkIjoiTEVDVlJQTVFUSy5tYXBzLmZsb29pZS5jb20iLCJpdGkiOmZhbHNlLCJpcnQiOmZhbHNlLCJpYXQiOjE2OTc3MjgzNzYsImV4cCI6MTY5NzczMDE3Nn0.R8wej3CC6UhNCjw4codfmnM3bwFH5tfOR28KMeIYX-Tace8blf2GlmwG5X_FEd5BeoiK6c4UxLO205qMGhHF5w"
    #
    # headers = {"Authorization": f"Bearer {token}"}
    # response = requests.get(
    #     "https://maps-api.apple.com/v1/geocode",
    #     params={"q": location},
    #     headers=headers,
    # )
    # print(response.json())
    # return response
