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
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from pathlib import Path
root = Path(__file__).parent

# Create a base class for declarative models
Base = declarative_base()
db_url = Path.joinpath(root, "..", "docs", "data", "records.db")

engine = create_engine(f"sqlite:///{db_url}", echo=False)

# Define a model
class ArrestLog(Base):
    __tablename__ = "arrestlogs"

    id = Column(Integer, primary_key=True)
    date_created = Column(DateTime, nullable=False)
    filename = Column(String, nullable=False)
    url = Column(String, nullable=True)
    pdf_processed = Column(Boolean, nullable=False, default=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# Define an event listener to set the date_created field before insert
@event.listens_for(ArrestLog, "before_insert")
def set_date_created(mapper, connection, target):
    target.date_created = datetime.utcnow()



def initialize_db():
    if os.path.exists("src/records.db"):
        return

    # Create the tables in the database
    Base.metadata.create_all(engine)

    # Define an event listener to set the date_created field before insert
    @event.listens_for(ArrestLog, 'before_insert')
    def set_date_created(mapper, connection, target):
        target.date_created = datetime.utcnow()

    # # Create a Session class for interacting with the database
    Session = sessionmaker(bind=engine)
    session = Session()
    session.close()

def record_in_database(url):
    """"""
    Session = sessionmaker(bind=engine)
    s = Session()
    count = s.query(ArrestLog).filter(ArrestLog.url == url).count()
    s.close()
    return count == 1

def save_record_to_db(url, filename):
    """"""
    Session = sessionmaker(bind=engine)
    s = Session()
    new_log = ArrestLog(**{"url": url, "filename": filename})
    s.add(new_log)
    s.commit()
    s.close()

