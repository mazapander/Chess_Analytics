from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.chess_service import import_all, import_month
from app.core import get_db, settings
from app.models import Game, Move
from app.schemas import GameDetail, GameRead, ImportRunRead, MoveRead

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get(f"{settings.api_v1_prefix}/games", response_model=list[GameRead])
def list_games(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    time_class: str | None = None,
    color: str | None = None,
    db: Session = Depends(get_db),
) -> list[Game]:
    stmt = select(Game).order_by(Game.played_at.desc()).offset(offset).limit(limit)
    if time_class:
        stmt = stmt.where(Game.time_class == time_class)
    if color:
        stmt = stmt.where(Game.player_color == color)
    return list(db.scalars(stmt).all())


@app.get(f"{settings.api_v1_prefix}/games/{{game_id}}", response_model=GameDetail)
def get_game(game_id: int, db: Session = Depends(get_db)) -> Game:
    game = db.scalar(
        select(Game).options(selectinload(Game.moves)).where(Game.id == game_id)
    )
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@app.get(f"{settings.api_v1_prefix}/games/{{game_id}}/moves", response_model=list[MoveRead])
def get_moves(game_id: int, db: Session = Depends(get_db)) -> list[Move]:
    exists = db.get(Game, game_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Game not found")
    return list(db.scalars(select(Move).where(Move.game_id == game_id).order_by(Move.ply)).all())


@app.post(f"{settings.api_v1_prefix}/imports/all", response_model=ImportRunRead)
def sync_all_games(db: Session = Depends(get_db)):
    return import_all(db, settings.chess_username)


@app.post(f"{settings.api_v1_prefix}/imports/{{year}}/{{month}}", response_model=ImportRunRead)
def sync_month(year: int, month: int, db: Session = Depends(get_db)):
    if year < 2007 or month < 1 or month > 12:
        raise HTTPException(status_code=422, detail="Invalid year or month")
    return import_month(db, settings.chess_username, year, month)
