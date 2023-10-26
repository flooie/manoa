from src.models import Document, Arrest, Charge, Person
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import json
import sqlalchemy
from js import alert
from src import pydom

def connect_to_database(is_echoed: False):
    """"""
    Base = sqlalchemy.orm.declarative_base()
    db_url = "data/manoa.db"
    engine = create_engine(f"sqlite:///{db_url}", echo=is_echoed)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def fetch_arrest_records(word_search):
    """"""
    session = connect_to_database(is_echoed=False)
    unique_locations = (
        session.query(Arrest.location, Arrest.longitude, Arrest.latitude)
        .group_by(Arrest.location)
            .filter(Arrest.location.like(f'%{word_search}%'))
            .all()
    )

    # Convert this tuple of tuples to list of lists and
    # exclude where we failed to find the location
    unique_list = [list(item) for item in unique_locations if item[1] != "0"]

    arrest_data_json = json.dumps(unique_list)
    return arrest_data_json
        