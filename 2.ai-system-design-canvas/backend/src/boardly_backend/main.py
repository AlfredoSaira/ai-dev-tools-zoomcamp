from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .db import Base, SessionLocal, engine
from .schemas import Board, Card, CardCreate, CardMove, CardUpdate, ColumnInfo
from .store import COLUMNS, CardStore

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Boardly API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_store(db: Session = Depends(get_db)) -> CardStore:
    return CardStore(db)


@app.get("/board", response_model=Board)
def get_board(store: CardStore = Depends(get_store)):
    return Board(
        columns=[ColumnInfo(**c) for c in COLUMNS],
        cards=[Card(**c) for c in store.list_cards()],
    )


@app.post("/cards", response_model=Card, status_code=status.HTTP_201_CREATED)
def create_card(payload: CardCreate, store: CardStore = Depends(get_store)):
    card = store.create(
        title=payload.title, description=payload.description, column=payload.column
    )
    return Card(**card)


@app.patch("/cards/{card_id}", response_model=Card)
def update_card(
    card_id: str, payload: CardUpdate, store: CardStore = Depends(get_store)
):
    card = store.update(card_id, title=payload.title, description=payload.description)
    if card is None:
        raise HTTPException(status_code=404, detail="Card not found")
    return Card(**card)


@app.patch("/cards/{card_id}/move", response_model=Card)
def move_card(card_id: str, payload: CardMove, store: CardStore = Depends(get_store)):
    card = store.update(card_id, column=payload.column)
    if card is None:
        raise HTTPException(status_code=404, detail="Card not found")
    return Card(**card)


@app.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(card_id: str, store: CardStore = Depends(get_store)):
    if not store.delete(card_id):
        raise HTTPException(status_code=404, detail="Card not found")
