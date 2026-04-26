"""Add role column to user table

Revision ID: add_role_to_user
Revises: 1a31ce608336
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = "add_role_to_user"
down_revision = "1a31ce608336"
branch_labels = None
depends_on = None


def upgrade():
    # Add role column with default value 'member'
    op.add_column(
        "user",
        sa.Column(
            "role",
            sa.VARCHAR(length=20),
            nullable=False,
            server_default="member"
        )
    )


def downgrade():
    op.drop_column("user", "role")