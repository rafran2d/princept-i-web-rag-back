"""add_column

Revision ID: 61dc8b83e6db
Revises: 07c4b256bdc6
Create Date: 2025-10-01 23:23:44.349280
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '61dc8b83e6db'
down_revision: Union[str, Sequence[str], None] = '07c4b256bdc6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define the enum type
status_enum = sa.Enum('uploaded', 'chunked', 'ready', 'failed', name='statusenum')
role_enum = sa.Enum('admin', 'user', name='roleenum')


def upgrade() -> None:
    """Upgrade schema."""

    #save it into the database
    status_enum.create(op.get_bind(), checkfirst=True)
    role_enum.create(op.get_bind(), checkfirst=True)

    
    op.add_column('documents', sa.Column('text', sa.String(), nullable=True))
    op.add_column('documents', sa.Column('status', status_enum, nullable=False))
    op.drop_column('documents', 'content')


    op.alter_column(
        'users',
        'role',
        existing_type=sa.VARCHAR(),
        type_=role_enum,
        existing_nullable=False,
        postgresql_using="role::roleenum"
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        'users',
        'role',
        existing_type=role_enum,
        type_=sa.VARCHAR(),
        existing_nullable=False,

    )

    op.add_column('documents', sa.Column('content', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('documents', 'status')
    op.drop_column('documents', 'text')

    status_enum.drop(op.get_bind(), checkfirst=True)
    role_enum.drop(op.get_bind(), checkfirst=True)
