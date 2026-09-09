"""add_ticket_fotos

Revision ID: f7e6d5c4b3a2
Revises: 4aa137b79dcc
Create Date: 2026-08-05 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7e6d5c4b3a2'
down_revision: Union[str, None] = '4aa137b79dcc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tickets', sa.Column('fotos', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('tickets', 'fotos')
