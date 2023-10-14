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
import html

# from sqlalchemy.ext.declarative import declarative_base
# sqlalchemy.orm.declarative_base()
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from js import document, Object
from pyscript import Element, display, HTML
from prettytable import PrettyTable
# from pyscript import document, when
# from js import Blob, window
# from pyodide import to_js

# Create a base class for declarative models
Base = declarative_base()
db_url = "sqlite:///data/records.db"
engine = create_engine(db_url, echo=False)

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

def query():
    Session = sessionmaker(bind=engine)
    s = Session()
    logs = s.query(ArrestLog).all()
    s.close()
    msg = document.getElementById("main")
    headline = document.createElement("h1")
    headline.innerText = f"{len(logs)} logs collected"
    msg.append(headline)
    table = PrettyTable(preserve_internal_border=True, border=True)
    table.field_names = ["Id", "Filename"]
    for row in logs:
        table.add_row([row.id, row.filename])
    text = table.get_html_string(format=True, border=True)
    my_element = document.querySelector(".leftside")
    my_element.innerHTML = html.unescape(text)
    table = document.querySelector("table")
    table.classList.add("table")
    table.classList.add("table-striped")
    table.classList.add("table-hover")


if __name__ == '__main__':
    query()