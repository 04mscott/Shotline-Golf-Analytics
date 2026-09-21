"""initial schema

Revision ID: 4d9120a30492
Revises: 
Create Date: 2026-09-21 03:41:34.510882

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pathlib import Path

SCHEMA_SQL = Path(__file__).parent.parent / "sql" / "0001_initial_schema.sql"


# revision identifiers, used by Alembic.
revision: str = '4d9120a30492'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.get_bind().exec_driver_sql(SCHEMA_SQL.read_text())


def downgrade() -> None:
    # Baseline only: wipes everything.
    op.execute("DROP SCHEMA public CASCADE")
    op.execute("CREATE SCHEMA public")
