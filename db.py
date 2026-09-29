"""
Lesson 4 - wrapping sqlite3 in a small class
============================================

Lesson 3 had SQL scattered all over a script. Here we put it in one
class so the API code never writes SQL directly. This separation
(routes <-> database) is the point of the lesson.

Notice the methods take Pydantic models (ShipmentBase / ShipmentUpdate)
as input - lesson 2 and lesson 3 meeting each other.
"""

import sqlite3

from schemas import ShipmentBase, ShipmentUpdate


class Database:
    def __init__(self, db_name):
        # check_same_thread=False is needed because FastAPI may handle
        # requests on different threads than the one that opened the
        # connection. Fine for learning; a real app uses a connection pool.
        self.con = sqlite3.connect(db_name, check_same_thread=False)
        self.cur = self.con.cursor()
        # make sure the table exists as soon as the object is built
        self.CreateTable("shipments")

    def CreateTable(self, name: str):
        # the table name comes from our own code, not from the user, so
        # the f-string here is safe. Never do this with user input.
        self.cur.execute(f"""
            CREATE TABLE IF NOT EXISTS
            {name} 
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            weight REAL,
            status TEXT)

         """)
        self.con.commit()

    def create_shipment(self, shipment: ShipmentBase):
        # insert
        # model_dump() turns the Pydantic object into a plain dict, and
        # we add the status ourselves since the client does not send it.
        self.cur.execute(
            """INSERT INTO shipments(weight,content,status) VALUES(:weight,:content,:status)""",
            {**shipment.model_dump(), "status": "Placed"},
        )
        self.con.commit()
        # lastrowid = the id AUTOINCREMENT just gave to the new row
        return self.cur.lastrowid

    def update_shipment(self, sid: int, shipment: ShipmentUpdate):
        self.cur.execute(
            """
            UPDATE shipments SET content = :content WHERE id = :id 
            """,
            {
                **shipment.model_dump(),
                "id": sid,
            },
        )
        self.con.commit()
        # rowcount = how many rows were changed. 0 means the id was wrong.
        return self.cur.rowcount


# quick manual test without starting the server:
# db = Database("test.db")
# db.CreateTable("ships")
