import os
from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    create_engine,
    event,
    Float,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from pathlib import Path
root = Path(__file__).parent
#
# # Create a base class for declarative models
# Base = declarative_base()
# db_url = Path.joinpath(root, "..", "docs", "data", "actions.db")
#
# engine = create_engine(f"sqlite:///{db_url}", echo=False)
#
# # # Define a model
# # class Arrest(Base):
# #     __tablename__ = "crimes"
# #
# #     id = Column(Integer, primary_key=True)
# #     date_created = Column(DateTime, nullable=False)
# #     # log - the arrest log information
# #     # person
# #     # date
# #     # time
# #     # race
# #     # age
# #
# # class Charge(Base):
# #     filename = Column(String, nullable=False)
# #     # arrest - id
# #     charge
# #     statute,
# #     location
# #     long
# #     lat
# #     officer
# #     court_info
# #     rel_date_time
# #     how_released
# #
# #
# #     def as_dict(self):
# #         return {c.name: getattr(self, c.name) for c in self.__table__.columns}
# #
# #
# # # Define an event listener to set the date_created field before insert
# # @event.listens_for(CrimeLog, "before_insert")
# # def set_date_created(mapper, connection, target):
# #     target.date_created = datetime.utcnow()
# #
# #
# #
# def initialize_db():
#     if os.path.exists("src/manoa.db"):
#         return
#
#     # Create the tables in the database
#     Base.metadata.create_all(engine)
#
#     # Define an event listener to set the date_created field before insert
#     @event.listens_for(CrimeLog, 'before_insert')
#     def set_date_created(mapper, connection, target):
#         target.date_created = datetime.utcnow()
#
#     # # Create a Session class for interacting with the database
#     Session = sessionmaker(bind=engine)
#     session = Session()
#     session.close()

#
# from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relationship, sessionmaker
#
# from pathlib import Path
# root = Path(__file__).parent
#
# # Create a base class for declarative models
#
# # Create an engine and establish a connection to your database
# Base = declarative_base()
#
# # Define the Record table
# class Record(Base):
#     __tablename__ = "record"
#
#     id = Column(Integer, primary_key=True)
#     date_created = Column(DateTime, nullable=False)
#     filename = Column(String, nullable=False)
#     url = Column(String, nullable=True)
#     pdf_processed = Column(Boolean, nullable=False, default=False)
#
#     def as_dict(self):
#         return {c.name: getattr(self, c.name) for c in self.__table__.columns}
#
# class Arrest(Base):
#     __tablename__ = 'arrest'
#
#     id = Column(Integer, primary_key=True)
#     # date
#     # time
#
#
#     # each arrest has a record log pdf
#     record_id = Column(Integer, ForeignKey('record.id'))
#     record = relationship("Record", backref="arrest")
#
#
# # Define the Person table
# class Person(Base):
#     __tablename__ = 'person'
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     # add other columns related to a person
#     # race
#     # age
#
#     arrest_id = Column(Integer, ForeignKey('arrest.id'))
#     arrest = relationship("Arrest", backref="persons")
#
# # Define the Crime table
# class Charge(Base):
#     __tablename__ = 'charges'
#
#     id = Column(Integer, primary_key=True)
#     charge_title = Column(String)
#     # location_parsed
#     # statute,
#     # location
#     # long
#     # lat
#     # court_info
#     # rel_date_time
#     # how_released
#
#     arrest_id = Column(Integer, ForeignKey('arrest.id'))
#
#     person_id = Column(Integer, ForeignKey('person.id'))
#     person = relationship("Person", backref="crimes")
#
#     officer_id = Column(Integer, ForeignKey('officer.id'))
#     officer = relationship("Officer", backref="crimes")
#
#
# # Define the Officer table
# class Officer(Base):
#     __tablename__ = 'officer'
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     # add other columns related to an officer
#
#
# def connect_to_database():
#     db_url = Path.joinpath(root, "..", "docs", "data", "manoa.db")
#     engine = create_engine(f"sqlite:///{db_url}", echo=True)
#
#     # Event listener for setting the date_created before inserting a new record
#     @event.listens_for(Document, "before_insert")
#     def set_date_created(mapper, connection, target):
#         target.date_created = datetime.utcnow()
#
#     Base.metadata.create_all(engine)
#     Session = sessionmaker(bind=engine)
#     session = Session()
#     return session

#
# if __name__ == '__main__':
#     connect_to_database()


from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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

class Location(Base):
    __tablename__ = 'location'

    id = Column(Integer, primary_key=True)
    location_string = Column(String)
    longitude = Column(String)
    latitude = Column(String)


class Charge(Base):
    __tablename__ = 'charge'

    id = Column(Integer, primary_key=True)
    charge = Column(String)
    court = Column(String)
    crime = Column(String)
    how_released = Column(String)
    # location = Column(String)
    rel_datetime = Column(String)
    statute = Column(String)
    date = Column(String)# to be moved here.
    time = Column(String)# to be moved here

    person_id = Column(Integer, ForeignKey('person.id'))
    officer_id = Column(Integer, ForeignKey('officer.id'))
    location_id = Column(Integer, ForeignKey('location.id'))

class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    race = Column(String)
    sex = Column(String)
    age = Column(String)
    date = Column(String)
    time = Column(String)
    document_id = Column(Integer, ForeignKey('document.id'))
    charges = relationship('Charge', backref='person')


def connect_to_database(is_echoed: True):
    # db_url = Path.joinpath(root, "..", "docs", "data", "manoa.db")
    # engine = create_engine(f"sqlite:///{db_url}", echo=is_echoed)
    db_url = Path.joinpath(root, "..", "data", "manoa.db")
    engine = create_engine(f"sqlite:///{db_url}", echo=False)

    # Event listener for setting the date_created before inserting a new record
    @event.listens_for(Document, "before_insert")
    def set_date_created(mapper, connection, target):
        target.date_created = datetime.utcnow()

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
#
# # Example usage
# if __name__ == '__main__':
#     # db_url = Path.joinpath(root, "..", "data", "records.db")
#     # db_url = ""
#     # # db_url = Path.joinpath(root, "..", "docs", "data", "manoa.db")
#     # engine = create_engine(f"sqlite:///{db_url}", echo=False)
#     # Base.metadata.create_all(engine)
#     from sqlalchemy import desc
# 
#     s = connect_to_database(is_echoed=True)
#     print(s)
#     logs = s.query(Document).all()
#     s.close()
#     print(logs)