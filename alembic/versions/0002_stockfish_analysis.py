"""Add Stockfish move analysis.

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "engine_analyses",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("game_id", sa.BigInteger(), sa.ForeignKey("games.id", ondelete="CASCADE"), nullable=False),
        sa.Column("move_id", sa.BigInteger(), sa.ForeignKey("moves.id", ondelete="CASCADE"), nullable=False),
        sa.Column("engine_name", sa.String(50), nullable=False, server_default="Stockfish"),
        sa.Column("engine_version", sa.String(50)),
        sa.Column("depth", sa.Integer(), nullable=False),
        sa.Column("evaluation_before_cp", sa.Integer()),
        sa.Column("evaluation_after_cp", sa.Integer()),
        sa.Column("mate_before", sa.Integer()),
        sa.Column("mate_after", sa.Integer()),
        sa.Column("best_move_uci", sa.String(10)),
        sa.Column("played_move_uci", sa.String(10), nullable=False),
        sa.Column("centipawn_loss", sa.Integer()),
        sa.Column("classification", sa.String(30)),
        sa.Column("principal_variation", sa.Text()),
        sa.Column("is_player_move", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("analyzed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("move_id", "engine_name", "depth", name="uq_engine_analysis_move_engine_depth"),
    )
    op.create_index("ix_engine_analyses_game_id", "engine_analyses", ["game_id"])
    op.create_index("ix_engine_analyses_move_id", "engine_analyses", ["move_id"])
    op.create_index("ix_engine_analyses_classification", "engine_analyses", ["classification"])
    op.create_index("ix_engine_analyses_analyzed_at", "engine_analyses", ["analyzed_at"])


def downgrade() -> None:
    op.drop_table("engine_analyses")
