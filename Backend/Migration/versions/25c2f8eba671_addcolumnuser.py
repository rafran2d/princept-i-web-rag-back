"""AddcolumnUser

Revision ID: 25c2f8eba671
Revises: 3a99fad3baaa
Create Date: 2025-10-15 13:06:48.890336

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25c2f8eba671'
down_revision: Union[str, Sequence[str], None] = '3a99fad3baaa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Définition de l'enum pour SQLAlchemy
status_user = sa.Enum("pending", "approved", "rejected", name="statususer")


def upgrade() -> None:
    """Upgrade schema in two steps to handle existing users."""

    status_user.create(op.get_bind(), checkfirst=True)

    op.add_column('users', sa.Column('status', status_user, nullable=True))

    op.execute("UPDATE users SET status='pending' WHERE status IS NULL")

    op.alter_column('users', 'status', nullable=False)


def downgrade() -> None:
    """Downgrade schema by removing the 'status' column."""

    op.drop_column('users', 'status')
    status_user.drop(op.get_bind(), checkfirst=True)
