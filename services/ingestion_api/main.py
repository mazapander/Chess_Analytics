from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.chess_service import import_all, import_month
from app.core import get_db, settings
from app.schemas import ImportRunRead

app = FastAPI(title=f"{settings.app_name} - Ingestion API", version="0.2.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ingestion-api"}


@app.post("/api/v1/imports/all", response_model=ImportRunRead)
def sync_all_games(db: Session = Depends(get_db)):
    return import_all(db, settings.chess_username)


@app.post("/api/v1/imports/{year}/{month}", response_model=ImportRunRead)
def sync_month(year: int, month: int, db: Session = Depends(get_db)):
    if year < 2007 or month < 1 or month > 12:
        raise HTTPException(status_code=422, detail="Invalid year or month")
    return import_month(db, settings.chess_username, year, month)
