"""alter tickets: nullable usuario, add contact fields

Revision ID: b2c3d4e5f6a7
Revises: 9a1b2c3d4e5f
Create Date: 2026-06-29 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "9a1b2c3d4e5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("tickets", "codigo_usuario", existing_type=sa.Integer(), nullable=True)
    op.drop_constraint("tickets_ibfk_2", "tickets", type_="foreignkey")
    op.create_foreign_key("fk_tickets_usuario", "tickets", "usuario", ["codigo_usuario"], ["codigo_usuario"], ondelete="SET NULL")
    op.add_column("tickets", sa.Column("nombre_contacto", sa.String(150), nullable=True))
    op.add_column("tickets", sa.Column("correo_contacto", sa.String(150), nullable=True))
    op.add_column("tickets", sa.Column("asunto", sa.String(200), nullable=True))


def downgrade() -> None:
    op.drop_column("tickets", "asunto")
    op.drop_column("tickets", "correo_contacto")
    op.drop_column("tickets", "nombre_contacto")
    op.drop_constraint("fk_tickets_usuario", "tickets", type_="foreignkey")
    op.create_foreign_key("tickets_ibfk_2", "tickets", "usuario", ["codigo_usuario"], ["codigo_usuario"], ondelete="CASCADE")
    op.alter_column("tickets", "codigo_usuario", existing_type=sa.Integer(), nullable=False)
