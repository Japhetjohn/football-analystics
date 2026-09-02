"""Init

Revision ID: 995227c245ae
Revises: 4d0c656a007c
Create Date: 2026-09-03 00:11:40.073116

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '995227c245ae'
down_revision: Union[str, Sequence[str], None] = '4d0c656a007c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
