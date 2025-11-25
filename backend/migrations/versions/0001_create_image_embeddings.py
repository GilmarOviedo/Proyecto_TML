"""create image_embeddings table

Revision ID: 0001_create_image_embeddings
Revises: 
Create Date: 2025-11-24 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_create_image_embeddings"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "image_embeddings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("image_path", sa.String(length=512), nullable=False),
        # Embedding completo como texto (cadena con lista de floats).
        # MySQL no tiene tipo VECTOR como pgvector, por eso usamos TEXT.
        sa.Column("embedding", sa.Text(), nullable=False),
        # Posición del vector dentro del índice FAISS (faiss_index.bin)
        sa.Column("faiss_index", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("image_path"),
    )


def downgrade() -> None:
    op.drop_table("image_embeddings")
