from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    create_engine,
    event, 
    ForeignKey,
)
from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from pathlib import Path
root = Path(__file__).parent

# Create a base class for declarative models
Base = declarative_base()
db_url = Path.joinpath(root, "..", "data", "manoa.db")
engine = create_engine(f"sqlite:///{db_url}", echo=False)

class Document(Base):
    __tablename__ = 'document'

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False, unique=True)

    date_created = Column(DateTime, nullable=False)
    url = Column(String, nullable=True, unique=True)
    pdf_processed = Column(Boolean, nullable=False, default=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in
                self.__table__.columns}

class Officer(Base):
    __tablename__ = 'officer'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Arrest(Base):
    __tablename__ = 'arrest'

    id = Column(Integer, primary_key=True)
    location = Column(String)
    longitude = Column(String)
    latitude = Column(String)
    location_error = Column(String)
    date = Column(String) # of Arrest
    time = Column(String) # of Arrest

class Charge(Base):
    __tablename__ = 'charge'

    id = Column(Integer, primary_key=True)
    charge = Column(String)
    court = Column(String)
    crime = Column(String)
    how_released = Column(String)
    rel_datetime = Column(String)
    statute = Column(String)

    person_id = Column(Integer, ForeignKey('person.id'))
    officer_id = Column(Integer, ForeignKey('officer.id'))
    arrest_id = Column(Integer, ForeignKey('arrest.id'))

class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    race = Column(String)
    sex = Column(String)
    age = Column(String)
    
    document_id = Column(Integer, ForeignKey('document.id'))
    charges = relationship('Charge', backref='person')


def initialize_db():

    db_url = Path.joinpath(root, "..", "data", "manoa.db")
    engine = create_engine(f"sqlite:///{db_url}", echo=False)

    # Create the tables in the database
    Base.metadata.create_all(engine)

    # Define an event listener to set the date_created field before insert
    @event.listens_for(Document, 'before_insert')
    def set_date_created(mapper, connection, target):
        target.date_created = datetime.utcnow()

    # # Create a Session class for interacting with the database
    Session = sessionmaker(bind=engine)
    session = Session()
    session.close()


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
