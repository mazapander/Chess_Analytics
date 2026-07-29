from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.analytics_service import build_overview
from app.core import get_db, settings
from app.models import Game, Move
from app.schemas import GameDetail, GameRead, MoveRead

app = FastAPI(title=f"{settings.app_name} - Analytics API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "analytics-api"}


@app.get("/api/v1/analytics/overview")
def overview(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    time_class: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    return build_overview(db, date_from=date_from, date_to=date_to, time_class=time_class)


@app.get("/api/v1/games", response_model=list[GameRead])
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


@app.get("/api/v1/games/{game_id}", response_model=GameDetail)
def get_game(game_id: int, db: Session = Depends(get_db)) -> Game:
    game = db.scalar(select(Game).options(selectinload(Game.moves)).where(Game.id == game_id))
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@app.get("/api/v1/games/{game_id}/moves", response_model=list[MoveRead])
def get_moves(game_id: int, db: Session = Depends(get_db)) -> list[Move]:
    if not db.get(Game, game_id):
        raise HTTPException(status_code=404, detail="Game not found")
    return list(db.scalars(select(Move).where(Move.game_id == game_id).order_by(Move.ply)).all())
