"""change_status_column

Revision ID: 7e5234fdf2d3
Revises: b3079753a76e
Create Date: 2025-10-07 10:35:13.759658

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e5234fdf2d3'
down_revision: Union[str, Sequence[str], None] = 'b3079753a76e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

status_enum_chat = sa.Enum('Usable','UNusable',name='statusenum_chat')

def upgrade() -> None:
    """Upgrade schema."""
    status_enum_chat.create(op.get_bind())
    op.drop_column('chats', 'status')
    op.add_column(
        'chats',
        sa.Column('status', status_enum_chat, nullable=False, server_default='Usable')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('chats', 'status')
    status_enum_chat.drop(op.get_bind())