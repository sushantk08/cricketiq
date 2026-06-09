"""Create initial database schema

Revision ID: 97c50adce210
Revises: aab20f60d7f9
Create Date: 2026-09-15 11:30:44.042772

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "97c50adce210"
down_revision: Union[str, Sequence[str], None] = "aab20f60d7f9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the application schema when it does not already exist."""
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # The actual table definitions are imported through the application's
    # SQLAlchemy models. We use their metadata to create only missing tables.
    from backend.app.database.session import Base
    import backend.app.models  # noqa: F401

    for table in Base.metadata.sorted_tables:
        if table.name not in existing_tables:
            table.create(bind=bind)


def downgrade() -> None:
    """Drop the application schema."""
    bind = op.get_bind()

    from backend.app.database.session import Base
    import backend.app.models  # noqa: F401

    for table in reversed(Base.metadata.sorted_tables):
        table.drop(bind=bind, checkfirst=True)