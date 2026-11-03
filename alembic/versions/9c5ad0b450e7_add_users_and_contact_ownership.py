"""add users and contact ownership

Revision ID: 9c5ad0b450e7
Revises: e07e8caf3121
Create Date: 2026-10-12 18:34:15.711382

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c5ad0b450e7'
down_revision: Union[str, Sequence[str], None] = 'e07e8caf3121'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("avatar", sa.String(length=255), nullable=True),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    # Спочатку додаємо user_id, дозволяючи NULL для старих контактів.
    op.add_column(
        "contacts",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )

    op.drop_constraint(
        op.f("contacts_email_key"),
        "contacts",
        type_="unique",
    )

    op.create_foreign_key(
        "fk_contacts_user_id_users",
        "contacts",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_contacts_user_id_users",
        "contacts",
        type_="foreignkey",
    )
    op.create_unique_constraint(
        op.f("contacts_email_key"),
        "contacts",
        ["email"],
        postgresql_nulls_not_distinct=False,
    )
    op.drop_column("contacts", "user_id")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    # ### end Alembic commands ###
