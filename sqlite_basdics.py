"""
Lesson 3 - plain sqlite3, no FastAPI at all
===========================================

Before wiring a database into the API we practise SQL on its own.
Python ships with sqlite3, so there is nothing to install and the whole
database is a single file on disk (sqlite.db).

The 4 operations you need (CRUD):
    CREATE -> INSERT
    READ   -> SELECT
    UPDATE -> UPDATE
    DELETE -> DELETE

Run it:
    python 03_raw_sqlite/sqlite_basics.py

Run it twice and notice the data is still there - unlike lesson 1 and 2,
this survives a restart.
"""

import sqlite3

# connect() opens the file, and creates it if it does not exist yet.
connection = sqlite3.connect("sqlite.db")

# a cursor is the object you actually run SQL statements with
cur = connection.cursor()


# --- CREATE TABLE ----------------------------------------------------------
# IF NOT EXISTS keeps this safe to run every time.
cur.execute("""
CREATE TABLE IF NOT EXISTS shipment(
    id INTEGER,
    content TEXT,
    weight REAL,
    status TEXT
)
""")
connection.commit()


# --- INSERT ----------------------------------------------------------------
cur.execute("""
INSERT INTO shipment VALUES (1270, "pulses", 10, "placed")
""")
# nothing is saved to the file until you commit()
connection.commit()


# --- READ ------------------------------------------------------------------
cur.execute("""
SELECT content FROM shipment WHERE id = 1270
""")
data = cur.fetchone()   # fetchone() = first row, fetchall() = every row
print("after insert:", data)


# --- UPDATE ----------------------------------------------------------------
# NEVER build SQL with f-strings or + - that is how SQL injection happens.
# Use named placeholders (:name) and pass a dict, sqlite3 escapes for you.
id = 1270
status = "out"

cur.execute(
    """
UPDATE shipment SET status = :status WHERE id = :id""",
    {"status": status, "id": id},
)
connection.commit()

cur.execute("SELECT status FROM shipment WHERE id = :id", {"id": id})
print("after update:", cur.fetchone())


# --- DELETE ----------------------------------------------------------------
cur.execute("""
DELETE FROM shipment WHERE id = 1270
""")
connection.commit()

cur.execute("SELECT * FROM shipment WHERE id = :id", {"id": id})
print("after delete:", cur.fetchone())   # None, the row is gone


# always close the connection when you are done
connection.close()
