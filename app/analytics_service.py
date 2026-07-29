from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from statistics import mean

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Game

DRAW_RESULTS = {
    "agreed",
    "repetition",
    "stalemate",
    "insufficient",
    "50move",
    "timevsinsufficient",
}


def _score(result: str | None) -> float:
    if result == "win":
        return 1.0
    if result in DRAW_RESULTS:
        return 0.5
    return 0.0


def _player_rating(game: Game) -> int | None:
    return game.white_rating if game.player_color == "white" else game.black_rating


def _opponent_rating(game: Game) -> int | None:
    return game.black_rating if game.player_color == "white" else game.white_rating


def _summary(games: list[Game]) -> dict:
    scores = [_score(game.player_result) for game in games]
    return {
        "games": len(games),
        "wins": sum(game.player_result == "win" for game in games),
        "draws": sum(game.player_result in DRAW_RESULTS for game in games),
        "losses": sum(_score(game.player_result) == 0 for game in games),
        "score_percentage": round(mean(scores) * 100, 2) if scores else None,
    }


def build_overview(
    db: Session,
    *,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    time_class: str | None = None,
) -> dict:
    stmt = select(Game).order_by(Game.played_at.asc())
    if date_from:
        stmt = stmt.where(Game.played_at >= date_from)
    if date_to:
        stmt = stmt.where(Game.played_at <= date_to)
    if time_class:
        stmt = stmt.where(Game.time_class == time_class)

    games = list(db.scalars(stmt).all())
    player_ratings = [rating for game in games if (rating := _player_rating(game)) is not None]
    opponent_ratings = [rating for game in games if (rating := _opponent_rating(game)) is not None]

    by_color = {
        color: _summary([game for game in games if game.player_color == color])
        for color in ("white", "black")
    }

    grouped: dict[str, list[Game]] = defaultdict(list)
    for game in games:
        grouped[game.time_class or "unknown"].append(game)

    by_time_class = [
        {"time_class": key, **_summary(subset)}
        for key, subset in sorted(grouped.items(), key=lambda item: len(item[1]), reverse=True)
    ]

    by_month_groups: dict[str, list[Game]] = defaultdict(list)
    for game in games:
        by_month_groups[game.played_at.strftime("%Y-%m")].append(game)
    monthly_trend = [
        {"month": month, **_summary(subset)}
        for month, subset in sorted(by_month_groups.items())
    ]

    opening_groups: dict[str, list[Game]] = defaultdict(list)
    for game in games:
        opening_groups[game.opening_name or "Unknown opening"].append(game)
    openings = [
        {"opening": opening, **_summary(subset)}
        for opening, subset in sorted(
            opening_groups.items(), key=lambda item: len(item[1]), reverse=True
        )[:15]
    ]

    return {
        **_summary(games),
        "average_player_rating": round(mean(player_ratings), 1) if player_ratings else None,
        "average_opponent_rating": round(mean(opponent_ratings), 1) if opponent_ratings else None,
        "by_color": by_color,
        "by_time_class": by_time_class,
        "monthly_trend": monthly_trend,
        "top_openings": openings,
    }
