from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251002_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "positions",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("position_id", sa.String(length=128), nullable=False),
        sa.Column("owner_address", sa.String(length=64), nullable=False),
        sa.Column("collateral_symbol", sa.String(length=32), nullable=False),
        sa.Column("collateral_amount", sa.String(length=64), nullable=False),
        sa.Column("debt_symbol", sa.String(length=32), nullable=False),
        sa.Column("debt_amount", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_positions_position_id", "positions", ["position_id"], unique=True)
    op.create_index("ix_positions_owner", "positions", ["owner_address"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_positions_owner", table_name="positions")
    op.drop_index("ix_positions_position_id", table_name="positions")
    op.drop_table("positions")
