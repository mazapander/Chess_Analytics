from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MoveRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ply: int
    move_number: int
    color: str
    san: str
    uci: str
    fen_before: str
    fen_after: str
    piece: str
    from_square: str
    to_square: str
    is_capture: bool
    is_check: bool
    is_castling: bool
    is_promotion: bool
    clock_seconds: float | None
    time_spent_seconds: float | None


class GameRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chess_com_url: str
    played_at: datetime
    time_class: str | None
    time_control: str | None
    rated: bool
    opening_name: str | None
    white_username: str
    white_rating: int | None
    white_result: str | None
    black_username: str
    black_rating: int | None
    black_result: str | None
    player_color: str
    player_result: str | None
    analysis_status: str


class GameDetail(GameRead):
    pgn: str
    final_fen: str | None
    moves: list[MoveRead]


class ImportRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    year: int | None
    month: int | None
    status: str
    archives_processed: int
    games_found: int
    games_created: int
    games_updated: int
    error_message: str | None
    started_at: datetime
    finished_at: datetime | None
