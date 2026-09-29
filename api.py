"""
Lesson 5 - FastAPI + SQLModel + dependency injection
====================================================

The final shape. Three new ideas:

    1. lifespan  - code that runs once on startup (and once on shutdown,
                   after the yield). We use it to create the tables.
    2. Depends() - FastAPI calls get_session() for us and passes the
                   result in. The endpoint never builds a session itself,
                   which makes it easy to test and impossible to leak.
    3. select()  - queries written in Python instead of SQL strings.

Run it:
    fastapi dev 05_sqlmodel_database/api.py

Exercise: add GET /shipment/{id}, PATCH and DELETE using
session.get(Shipment, id), session.delete(...) and session.commit().
"""

from fastapi import Depends, FastAPI
from contextlib import asynccontextmanager

from sqlmodel import Session, select
from Database.models import Shipment
from Database.session import create_db_and_table, get_session
from schemas import Ships

@asynccontextmanager
async def lifespan(app:FastAPI):
    # everything before yield runs at startup
    create_db_and_table()
    yield
    # everything after yield would run at shutdown

app=FastAPI(lifespan=lifespan)


@app.get("/")
def home():
    return {"message":"hello db"}


@app.post("/new_shipment")
def new_shipment(data:Ships,session:Session=Depends(get_session)):
    # model_validate turns the incoming Ships into a Shipment table row
    shipment = Shipment.model_validate(data.model_dump())
    session.add(shipment)      # stage it
    session.commit()           # write it to the file
    session.refresh(shipment)  # reload it so we get the generated id
    return shipment

@app.get("/get-shipment")
def get_shipment(session:Session=Depends(get_session)):
    # SELECT * FROM shipment, written in Python
    statement = select(Shipment)
    shipment= session.exec(statement).all()
    return shipment
