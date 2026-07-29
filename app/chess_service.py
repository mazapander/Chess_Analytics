from __future__ import annotations

import io
from datetime import UTC, datetime
from urllib.parse import unquote

import chess
import chess.pgn
import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import settings
from app.models import Game, ImportRun, ImportStatus, Move


class ChessComClient:
    def __init__(self) -> None:
        self.headers = {"User-Agent": settings.chess_user_agent, "Accept": "application/json"}

    def get_archives(self, username: str) -> list[str]:
        url = f"{settings.chess_api_base_url}/player/{username}/games/archives"
        with httpx.Client(headers=self.headers, timeout=30.0, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.json().get("archives", [])

    def get_month_games(self, username: str, year: int, month: int) -> list[dict]:
        url = f"{settings.chess_api_base_url}/player/{username}/games/{year}/{month:02d}"
        with httpx.Client(headers=self.headers, timeout=60.0, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.json().get("games", [])


def _opening_name(eco_url: str | None) -> str | None:
    if not eco_url:
        return None
    slug = unquote(eco_url.rstrip("/").split("/")[-1])
    return slug.replace("-", " ").strip() or None


def _clock_seconds(node: chess.pgn.GameNode) -> float | None:
    try:
        return node.clock()
    except (ValueError, TypeError):
        return None


def parse_moves(pgn_text: str) -> tuple[list[dict], str | None]:
    game = chess.pgn.read_game(io.StringIO(pgn_text))
    if game is None:
        return [], None

    board = game.board()
    parsed: list[dict] = []
    previous_clock: dict[chess.Color, float | None] = {chess.WHITE: None, chess.BLACK: None}

    for ply, node in enumerate(game.mainline(), start=1):
        move = node.move
        color = board.turn
        fen_before = board.fen()
        san = board.san(move)
        piece = board.piece_at(move.from_square)
        is_capture = board.is_capture(move)
        is_castling = board.is_castling(move)
        clock = _clock_seconds(node)
        last_clock = previous_clock[color]
        time_spent = None if clock is None or last_clock is None else max(last_clock - clock, 0.0)

        board.push(move)
        parsed.append(
            {
                "ply": ply,
                "move_number": (ply + 1) // 2,
                "color": "white" if color == chess.WHITE else "black",
                "san": san,
                "uci": move.uci(),
                "fen_before": fen_before,
                "fen_after": board.fen(),
                "piece": chess.piece_name(piece.piece_type) if piece else "unknown",
                "from_square": chess.square_name(move.from_square),
                "to_square": chess.square_name(move.to_square),
                "is_capture": is_capture,
                "is_check": board.is_check(),
                "is_castling": is_castling,
                "is_promotion": move.promotion is not None,
                "clock_seconds": clock,
                "time_spent_seconds": time_spent,
            }
        )
        previous_clock[color] = clock

    return parsed, board.fen()


def upsert_game(db: Session, payload: dict, username: str) -> tuple[Game, bool]:
    url = payload["url"]
    game = db.scalar(select(Game).where(Game.chess_com_url == url))
    created = game is None
    if game is None:
        game = Game(chess_com_url=url, pgn="", played_at=datetime.now(UTC), end_time_unix=0,
                    white_username="", black_username="", player_color="white")
        db.add(game)

    white = payload.get("white", {})
    black = payload.get("black", {})
    accuracy = payload.get("accuracies", {})
    pgn_text = payload.get("pgn", "")
    moves, parsed_final_fen = parse_moves(pgn_text)
    normalized_username = username.lower()
    player_color = "white" if white.get("username", "").lower() == normalized_username else "black"
    player = white if player_color == "white" else black
    end_time = int(payload.get("end_time", 0))

    game.pgn = pgn_text
    game.played_at = datetime.fromtimestamp(end_time, tz=UTC)
    game.end_time_unix = end_time
    game.time_class = payload.get("time_class")
    game.time_control = payload.get("time_control")
    game.rules = payload.get("rules")
    game.rated = bool(payload.get("rated", False))
    game.initial_setup = payload.get("initial_setup")
    game.final_fen = payload.get("fen") or parsed_final_fen
    game.eco_url = payload.get("eco")
    game.opening_name = _opening_name(payload.get("eco"))
    game.white_username = white.get("username", "")
    game.white_rating = white.get("rating")
    game.white_result = white.get("result")
    game.white_accuracy = accuracy.get("white")
    game.black_username = black.get("username", "")
    game.black_rating = black.get("rating")
    game.black_result = black.get("result")
    game.black_accuracy = accuracy.get("black")
    game.player_color = player_color
    game.player_result = player.get("result")

    game.moves.clear()
    game.moves.extend(Move(**item) for item in moves)
    db.flush()
    return game, created


def import_month(db: Session, username: str, year: int, month: int) -> ImportRun:
    run = ImportRun(username=username, year=year, month=month, status=ImportStatus.running)
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        games = ChessComClient().get_month_games(username, year, month)
        run.archives_processed = 1
        run.games_found = len(games)
        for payload in games:
            _, created = upsert_game(db, payload, username)
            if created:
                run.games_created += 1
            else:
                run.games_updated += 1
        run.status = ImportStatus.completed
        run.finished_at = datetime.now(UTC)
        db.commit()
    except Exception as exc:
        db.rollback()
        run = db.get(ImportRun, run.id)
        run.status = ImportStatus.failed
        run.error_message = str(exc)
        run.finished_at = datetime.now(UTC)
        db.commit()
        raise
    db.refresh(run)
    return run


def import_all(db: Session, username: str) -> ImportRun:
    run = ImportRun(username=username, status=ImportStatus.running)
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        archives = ChessComClient().get_archives(username)
        for archive in archives:
            year, month = map(int, archive.rstrip("/").split("/")[-2:])
            games = ChessComClient().get_month_games(username, year, month)
            run.archives_processed += 1
            run.games_found += len(games)
            for payload in games:
                _, created = upsert_game(db, payload, username)
                if created:
                    run.games_created += 1
                else:
                    run.games_updated += 1
            db.commit()
        run.status = ImportStatus.completed
        run.finished_at = datetime.now(UTC)
        db.commit()
    except Exception as exc:
        db.rollback()
        run = db.get(ImportRun, run.id)
        run.status = ImportStatus.failed
        run.error_message = str(exc)
        run.finished_at = datetime.now(UTC)
        db.commit()
        raise
    db.refresh(run)
    return run
