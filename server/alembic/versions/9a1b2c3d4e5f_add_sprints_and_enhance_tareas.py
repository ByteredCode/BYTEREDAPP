"""add sprints table and enhance tareas

Revision ID: 9a1b2c3d4e5f
Revises: 3e03f2cf94fe
Create Date: 2026-06-29 14:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9a1b2c3d4e5f"
down_revision: Union[str, None] = "3e03f2cf94fe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sprints",
        sa.Column("codigo_sprint", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(length=150), nullable=False),
        sa.Column("objetivo", sa.Text(), nullable=True),
        sa.Column("fecha_inicio", sa.Date(), nullable=True),
        sa.Column("fecha_fin", sa.Date(), nullable=True),
        sa.Column(
            "estado",
            sa.Enum("Planificado", "Activo", "Completado", name="sprint_estado_enum"),
            nullable=True,
        ),
        sa.Column("codigo_empresa", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["codigo_empresa"], ["empresa.codigo_empresa"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("codigo_sprint"),
    )
    op.add_column(
        "tareas",
        sa.Column(
            "prioridad",
            sa.Enum("Baja", "Media", "Alta", "Critica", name="prioridad_enum"),
            nullable=True,
        ),
    )
    op.add_column(
        "tareas",
        sa.Column("orden", sa.Integer(), nullable=True),
    )
    op.add_column(
        "tareas",
        sa.Column("fecha_limite", sa.Date(), nullable=True),
    )
    op.add_column(
        "tareas",
        sa.Column("codigo_sprint", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_tareas_codigo_sprint",
        "tareas",
        "sprints",
        ["codigo_sprint"],
        ["codigo_sprint"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_tareas_codigo_sprint", "tareas", type_="foreignkey")
    op.drop_column("tareas", "codigo_sprint")
    op.drop_column("tareas", "fecha_limite")
    op.drop_column("tareas", "orden")
    op.drop_column("tareas", "prioridad")
    op.drop_table("sprints")
