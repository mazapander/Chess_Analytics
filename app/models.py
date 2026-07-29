from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base


class AnalysisStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class ImportStatus(str, enum.Enum):
    running = "running"
    completed = "completed"
    failed = "failed"


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    chess_com_url: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    pgn: Mapped[str] = mapped_column(Text)
    played_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    end_time_unix: Mapped[int] = mapped_column(BigInteger, index=True)
    time_class: Mapped[str | None] = mapped_column(String(30), index=True)
    time_control: Mapped[str | None] = mapped_column(String(50))
    rules: Mapped[str | None] = mapped_column(String(30))
    rated: Mapped[bool] = mapped_column(Boolean, default=False)
    initial_setup: Mapped[str | None] = mapped_column(Text)
    final_fen: Mapped[str | None] = mapped_column(Text)
    eco_url: Mapped[str | None] = mapped_column(String(500))
    opening_name: Mapped[str | None] = mapped_column(String(255), index=True)
    white_username: Mapped[str] = mapped_column(String(100), index=True)
    white_rating: Mapped[int | None] = mapped_column(Integer)
    white_result: Mapped[str | None] = mapped_column(String(50))
    white_accuracy: Mapped[float | None] = mapped_column(Float)
    black_username: Mapped[str] = mapped_column(String(100), index=True)
    black_rating: Mapped[int | None] = mapped_column(Integer)
    black_result: Mapped[str | None] = mapped_column(String(50))
    black_accuracy: Mapped[float | None] = mapped_column(Float)
    player_color: Mapped[str] = mapped_column(String(5), index=True)
    player_result: Mapped[str | None] = mapped_column(String(50), index=True)
    analysis_status: Mapped[AnalysisStatus] = mapped_column(
        Enum(AnalysisStatus, name="analysis_status"), default=AnalysisStatus.pending, index=True
    )
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    moves: Mapped[list[Move]] = relationship(
        back_populates="game", cascade="all, delete-orphan", order_by="Move.ply"
    )

    __table_args__ = (
        Index("ix_games_time_class_played_at", "time_class", "played_at"),
    )


class Move(Base):
    __tablename__ = "moves"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), index=True)
    ply: Mapped[int] = mapped_column(Integer)
    move_number: Mapped[int] = mapped_column(Integer)
    color: Mapped[str] = mapped_column(String(5), index=True)
    san: Mapped[str] = mapped_column(String(30))
    uci: Mapped[str] = mapped_column(String(10))
    fen_before: Mapped[str] = mapped_column(Text)
    fen_after: Mapped[str] = mapped_column(Text)
    piece: Mapped[str] = mapped_column(String(20))
    from_square: Mapped[str] = mapped_column(String(2))
    to_square: Mapped[str] = mapped_column(String(2))
    is_capture: Mapped[bool] = mapped_column(Boolean, default=False)
    is_check: Mapped[bool] = mapped_column(Boolean, default=False)
    is_castling: Mapped[bool] = mapped_column(Boolean, default=False)
    is_promotion: Mapped[bool] = mapped_column(Boolean, default=False)
    clock_seconds: Mapped[float | None] = mapped_column(Float)
    time_spent_seconds: Mapped[float | None] = mapped_column(Float)

    game: Mapped[Game] = relationship(back_populates="moves")

    __table_args__ = (
        Index("uq_moves_game_ply", "game_id", "ply", unique=True),
    )


class ImportRun(Base):
    __tablename__ = "import_runs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), index=True)
    year: Mapped[int | None] = mapped_column(Integer)
    month: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[ImportStatus] = mapped_column(
        Enum(ImportStatus, name="import_status"), default=ImportStatus.running, index=True
    )
    archives_processed: Mapped[int] = mapped_column(Integer, default=0)
    games_found: Mapped[int] = mapped_column(Integer, default=0)
    games_created: Mapped[int] = mapped_column(Integer, default=0)
    games_updated: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
