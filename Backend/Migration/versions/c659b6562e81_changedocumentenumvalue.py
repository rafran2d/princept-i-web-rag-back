"""ChangeDocumentEnumValue

Revision ID: c659b6562e81
Revises: ebb1ff731f24
Create Date: 2025-10-13 15:11:19.645889
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision: str = 'c659b6562e81'
down_revision: Union[str, Sequence[str], None] = 'ebb1ff731f24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add new values to existing enum instead of recreating it
    op.execute("ALTER TYPE statusenum ADD VALUE IF NOT EXISTS 'pending'")
    op.execute("ALTER TYPE statusenum ADD VALUE IF NOT EXISTS 'charged'")


def downgrade():
    # Recréer l'ancien type
    old_status_enum = sa.Enum('uploaded', 'chunked', 'ready', 'failed', name='statusenum_old')
    old_status_enum.create(op.get_bind(), checkfirst=False)

    op.execute("""
        ALTER TABLE documents
        ALTER COLUMN status TYPE statusenum_old
        USING status::text::statusenum_old;
    """)

    # Supprimer le nouveau type
    op.execute("DROP TYPE statusenum;")
