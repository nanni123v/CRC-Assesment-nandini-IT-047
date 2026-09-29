from fastapi import FastAPI, HTTPException, status
from sqlmodel import SQLModel, Field, Session, create_engine, select
from enum import Enum
from typing import Optional


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="College Lost & Found API",
    description="API for managing lost and found items on campus",
    version="1.0.0"
)


# =========================================================
# STATUS ENUM
# =========================================================

class ItemStatus(str, Enum):
    Lost = "Lost"
    Found = "Found"
    Returned = "Returned"


# =========================================================
# ITEM DATABASE MODEL
# =========================================================

class Item(SQLModel, table=True):

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    title: str
    description: str
    category: str
    location: str
    reported_by: str
    status: ItemStatus


# =========================================================
# DATABASE
# =========================================================

sqlite_url = "sqlite:///lost_found.db"

engine = create_engine(
    sqlite_url,
    echo=True
)


# =========================================================
# CREATE TABLE WHEN APPLICATION STARTS
# =========================================================

@app.on_event("startup")
def create_tables():

    SQLModel.metadata.create_all(engine)


# =========================================================
# 1. POST /items
# CREATE NEW LOST/FOUND ITEM
# =========================================================

@app.post(
    "/items",
    response_model=Item,
    status_code=status.HTTP_201_CREATED,
    tags=["Items"]
)
def create_item(item: Item):

    # Title validation
    if not item.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title must not be empty"
        )

    # Description validation
    if len(item.description.strip()) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Description must contain meaningful text"
        )

    with Session(engine) as session:

        session.add(item)
        session.commit()
        session.refresh(item)

        return item


# =========================================================
# 2. GET /items
# GET ALL ITEMS
# =========================================================

@app.get(
    "/items",
    response_model=list[Item],
    tags=["Items"]
)
def get_all_items():

    with Session(engine) as session:

        statement = select(Item)

        items = session.exec(statement).all()

        return items


# =========================================================
# 3. GET /items/{item_id}
# GET ONE ITEM
# =========================================================

@app.get(
    "/items/{item_id}",
    response_model=Item,
    tags=["Items"]
)
def get_item(item_id: int):

    with Session(engine) as session:

        item = session.get(Item, item_id)

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )

        return item


# =========================================================
# 4. PUT /items/{item_id}
# UPDATE ITEM
# =========================================================

@app.put(
    "/items/{item_id}",
    response_model=Item,
    tags=["Items"]
)
def update_item(item_id: int, updated_item: Item):

    # Validate title
    if not updated_item.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title must not be empty"
        )

    # Validate description
    if len(updated_item.description.strip()) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Description must contain meaningful text"
        )

    with Session(engine) as session:

        item = session.get(Item, item_id)

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )

        item.title = updated_item.title
        item.description = updated_item.description
        item.category = updated_item.category
        item.location = updated_item.location
        item.reported_by = updated_item.reported_by
        item.status = updated_item.status

        session.add(item)
        session.commit()
        session.refresh(item)

        return item


# =========================================================
# 5. DELETE /items/{item_id}
# DELETE ITEM
# =========================================================

@app.delete(
    "/items/{item_id}",
    tags=["Items"]
)
def delete_item(item_id: int):

    with Session(engine) as session:

        item = session.get(Item, item_id)

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )

        session.delete(item)
        session.commit()

        return {
            "message": "Item deleted successfully",
            "item_id": item_id
        }


# =========================================================
# 6. GET /items/status/{status}
# FILTER BY STATUS
# =========================================================

@app.get(
    "/items/status/{status}",
    response_model=list[Item],
    tags=["Filter"]
)
def get_items_by_status(status: ItemStatus):

    with Session(engine) as session:

        statement = select(Item).where(
            Item.status == status
        )

        items = session.exec(statement).all()

        return items


# =========================================================
# 7. GET /items/category/{category}
# FILTER BY CATEGORY
# =========================================================

@app.get(
    "/items/category/{category}",
    response_model=list[Item],
    tags=["Filter"]
)
def get_items_by_category(category: str):

    with Session(engine) as session:

        statement = select(Item).where(
            Item.category == category
        )

        items = session.exec(statement).all()

        return items