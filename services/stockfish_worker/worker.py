from __future__ import annotations

import logging
import os
import time
from contextlib import closing

import chess
import chess.engine
from sqlalchemy import select, text

from app.core import SessionLocal
from app.models import AnalysisStatus, Game, Move

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("stockfish-worker")

STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", "/usr/games/stockfish")
ANALYSIS_DEPTH = int(os.getenv("STOCKFISH_DEPTH", "14"))
POLL_SECONDS = int(os.getenv("STOCKFISH_POLL_SECONDS", "10"))
MATE_SCORE = 100_000


def score_value(score: chess.engine.PovScore, color: chess.Color) -> tuple[int | None, int | None]:
    pov = score.pov(color)
    if pov.is_mate():
        return None, pov.mate()
    return pov.score(mate_score=MATE_SCORE), None


def classify(cpl: int | None) -> str | None:
    if cpl is None:
        return None
    if cpl < 25:
        return "best_or_excellent"
    if cpl < 60:
        return "good"
    if cpl < 120:
        return "inaccuracy"
    if cpl < 250:
        return "mistake"
    return "blunder"


def analyze_game(engine: chess.engine.SimpleEngine, game: Game, moves: list[Move]) -> None:
    player_color = chess.WHITE if game.player_color == "white" else chess.BLACK

    with closing(SessionLocal()) as db:
        try:
            db.execute(
                text("UPDATE games SET analysis_status = 'processing' WHERE id = :game_id"),
                {"game_id": game.id},
            )
            db.commit()

            for move in moves:
                if (move.color == "white") != player_color:
                    continue

                existing = db.execute(
                    text(
                        "SELECT 1 FROM engine_analyses "
                        "WHERE move_id = :move_id AND engine_name = 'Stockfish' AND depth = :depth"
                    ),
                    {"move_id": move.id, "depth": ANALYSIS_DEPTH},
                ).first()
                if existing:
                    continue

                board_before = chess.Board(move.fen_before)
                played = chess.Move.from_uci(move.uci)
                before = engine.analyse(
                    board_before,
                    chess.engine.Limit(depth=ANALYSIS_DEPTH),
                    multipv=1,
                )
                best_move = before.get("pv", [None])[0]
                before_cp, mate_before = score_value(before["score"], player_color)

                board_after = chess.Board(move.fen_after)
                after = engine.analyse(board_after, chess.engine.Limit(depth=ANALYSIS_DEPTH))
                after_cp, mate_after = score_value(after["score"], player_color)

                cpl = None
                if before_cp is not None and after_cp is not None:
                    cpl = max(0, before_cp - after_cp)

                pv = " ".join(item.uci() for item in before.get("pv", [])[:8])
                db.execute(
                    text(
                        """
                        INSERT INTO engine_analyses (
                            game_id, move_id, engine_name, depth,
                            evaluation_before_cp, evaluation_after_cp,
                            mate_before, mate_after, best_move_uci,
                            played_move_uci, centipawn_loss, classification,
                            principal_variation, is_player_move
                        ) VALUES (
                            :game_id, :move_id, 'Stockfish', :depth,
                            :before_cp, :after_cp, :mate_before, :mate_after,
                            :best_move, :played_move, :cpl, :classification,
                            :pv, true
                        )
                        ON CONFLICT (move_id, engine_name, depth) DO NOTHING
                        """
                    ),
                    {
                        "game_id": game.id,
                        "move_id": move.id,
                        "depth": ANALYSIS_DEPTH,
                        "before_cp": before_cp,
                        "after_cp": after_cp,
                        "mate_before": mate_before,
                        "mate_after": mate_after,
                        "best_move": best_move.uci() if best_move else None,
                        "played_move": played.uci(),
                        "cpl": cpl,
                        "classification": classify(cpl),
                        "pv": pv,
                    },
                )
                db.commit()

            db.execute(
                text("UPDATE games SET analysis_status = 'completed' WHERE id = :game_id"),
                {"game_id": game.id},
            )
            db.commit()
            logger.info("Analyzed game %s", game.id)
        except Exception:
            db.rollback()
            db.execute(
                text("UPDATE games SET analysis_status = 'failed' WHERE id = :game_id"),
                {"game_id": game.id},
            )
            db.commit()
            logger.exception("Failed to analyze game %s", game.id)


def next_game() -> tuple[Game, list[Move]] | None:
    with closing(SessionLocal()) as db:
        game = db.scalar(
            select(Game)
            .where(Game.analysis_status.in_([AnalysisStatus.pending, AnalysisStatus.failed]))
            .order_by(Game.played_at.desc())
            .limit(1)
        )
        if not game:
            return None
        moves = list(db.scalars(select(Move).where(Move.game_id == game.id).order_by(Move.ply)).all())
        db.expunge(game)
        for move in moves:
            db.expunge(move)
        return game, moves


def run() -> None:
    logger.info("Starting Stockfish worker at depth %s", ANALYSIS_DEPTH)
    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
        while True:
            job = next_game()
            if not job:
                time.sleep(POLL_SECONDS)
                continue
            analyze_game(engine, *job)


if __name__ == "__main__":
    run()
