"""add_index_embedding_model

Revision ID: 63e6fb8f3385
Revises: 61dc8b83e6db
Create Date: 2025-10-06 10:37:08.308364

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63e6fb8f3385'
down_revision: Union[str, Sequence[str], None] = '61dc8b83e6db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('''
        CREATE INDEX IF NOT EXISTS embeddings_vector_hnsw
        ON embeddings
        USING hnsw (vector vector_l2_ops)
        WITH (m = 16, ef_construction = 64);
    ''')

def downgrade() -> None:
    """Downgrade schema."""
    op.execute('DROP INDEX IF EXISTS embeddings_vector_hnsw;')

