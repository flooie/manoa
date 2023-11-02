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

    charges = relationship('Charge', backref='officer')


class Arrest(Base):
    __tablename__ = 'arrest'

    id = Column(Integer, primary_key=True)
    location = Column(String)
    longitude = Column(String)
    latitude = Column(String)
    location_error = Column(String)
    date = Column(String) # of Arrest
    time = Column(String) # of Arrest
    
    charges = relationship('Charge', backref='arrest')

    def as_dict(self):
        # charges_data = [charge.as_dict() for charge in self.charges]

        data = {
            'id': self.id,
            'location': self.location,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'location_error': self.location_error,
            'date': self.date,
            'time': self.time,
            'charges': len(self.charges)
        }
        return data
    
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

    def as_dict(self):
        data = {
            'id': self.id,
            'charge': self.charge,
            'court': self.court,
            'crime': self.crime,
            'how_released': self.how_released,
            'rel_datetime': self.rel_datetime,
            'statute': self.statute,
            'person': {
                'id': self.person.id,
                'name': self.person.name,
                'race': self.person.race,
                'sex': self.person.sex,
                'age': self.person.age,  
                "other": self.person.document_id
                
            },
            'officer': {
                'id': self.officer.id,
                'name': self.officer.name
            },
            'arrest': {
                'id': self.arrest.id,
                'location': self.arrest.location,
                'longitude': self.arrest.longitude,
                'latitude': self.arrest.latitude,
                'location_error': self.arrest.location_error,
                'date': self.arrest.date,
                'time': self.arrest.time
            }
        }
        return data

class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    race = Column(String)
    sex = Column(String)
    age = Column(String)
    
    document_id = Column(Integer, ForeignKey('document.id'))
    charges = relationship('Charge', backref='person')


def search_partial_matches(session, search_term):
    results = (
        session.query(Charge)
        .join(Person)
        .filter(
            Charge.charge.ilike(f"%{search_term}%")
            | Person.name.ilike(f"%{search_term}%")
            | Charge.crime.ilike(f"%{search_term}%")
            | Arrest.location.ilike(f"%{search_term}%")
        )
        .all()
    )
    return results


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
