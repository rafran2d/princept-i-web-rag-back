"""merge heads

Revision ID: 036023493380
Revises: 7e5234fdf2d3, 83e83bfb0b01
Create Date: 2025-10-07 10:49:13.188457

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '036023493380'
down_revision: Union[str, Sequence[str], None] = ('7e5234fdf2d3', '83e83bfb0b01')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
