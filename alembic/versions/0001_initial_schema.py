"""Initial schema.

Revision ID: 0001
Revises:
Create Date: 2026-07-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

analysis_status = sa.Enum("pending", "processing", "completed", "failed", name="analysis_status")
import_status = sa.Enum("running", "completed", "failed", name="import_status")


def upgrade() -> None:
    analysis_status.create(op.get_bind(), checkfirst=True)
    import_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "games",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("chess_com_url", sa.String(500), nullable=False),
        sa.Column("pgn", sa.Text(), nullable=False),
        sa.Column("played_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time_unix", sa.BigInteger(), nullable=False),
        sa.Column("time_class", sa.String(30)),
        sa.Column("time_control", sa.String(50)),
        sa.Column("rules", sa.String(30)),
        sa.Column("rated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("initial_setup", sa.Text()),
        sa.Column("final_fen", sa.Text()),
        sa.Column("eco_url", sa.String(500)),
        sa.Column("opening_name", sa.String(255)),
        sa.Column("white_username", sa.String(100), nullable=False),
        sa.Column("white_rating", sa.Integer()),
        sa.Column("white_result", sa.String(50)),
        sa.Column("white_accuracy", sa.Float()),
        sa.Column("black_username", sa.String(100), nullable=False),
        sa.Column("black_rating", sa.Integer()),
        sa.Column("black_result", sa.String(50)),
        sa.Column("black_accuracy", sa.Float()),
        sa.Column("player_color", sa.String(5), nullable=False),
        sa.Column("player_result", sa.String(50)),
        sa.Column("analysis_status", analysis_status, nullable=False, server_default="pending"),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("chess_com_url"),
    )
    for column in ["chess_com_url", "played_at", "end_time_unix", "time_class", "opening_name", "white_username", "black_username", "player_color", "player_result", "analysis_status"]:
        op.create_index(f"ix_games_{column}", "games", [column])
    op.create_index("ix_games_time_class_played_at", "games", ["time_class", "played_at"])

    op.create_table(
        "moves",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("game_id", sa.BigInteger(), sa.ForeignKey("games.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ply", sa.Integer(), nullable=False),
        sa.Column("move_number", sa.Integer(), nullable=False),
        sa.Column("color", sa.String(5), nullable=False),
        sa.Column("san", sa.String(30), nullable=False),
        sa.Column("uci", sa.String(10), nullable=False),
        sa.Column("fen_before", sa.Text(), nullable=False),
        sa.Column("fen_after", sa.Text(), nullable=False),
        sa.Column("piece", sa.String(20), nullable=False),
        sa.Column("from_square", sa.String(2), nullable=False),
        sa.Column("to_square", sa.String(2), nullable=False),
        sa.Column("is_capture", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_check", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_castling", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_promotion", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("clock_seconds", sa.Float()),
        sa.Column("time_spent_seconds", sa.Float()),
    )
    op.create_index("ix_moves_game_id", "moves", ["game_id"])
    op.create_index("ix_moves_color", "moves", ["color"])
    op.create_index("uq_moves_game_ply", "moves", ["game_id", "ply"], unique=True)

    op.create_table(
        "import_runs",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("year", sa.Integer()),
        sa.Column("month", sa.Integer()),
        sa.Column("status", import_status, nullable=False, server_default="running"),
        sa.Column("archives_processed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("games_found", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("games_created", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("games_updated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_import_runs_username", "import_runs", ["username"])
    op.create_index("ix_import_runs_status", "import_runs", ["status"])


def downgrade() -> None:
    op.drop_table("import_runs")
    op.drop_table("moves")
    op.drop_table("games")
    import_status.drop(op.get_bind(), checkfirst=True)
    analysis_status.drop(op.get_bind(), checkfirst=True)
