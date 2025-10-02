from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251002_0003"
down_revision = "20251002_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chain_events",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("block_number", sa.Integer(), nullable=False),
        sa.Column("tx_hash", sa.String(length=80), nullable=False),
        sa.Column("log_index", sa.Integer(), nullable=False),
        sa.Column("event_name", sa.String(length=64), nullable=False),
        sa.Column("contract_address", sa.String(length=64), nullable=False),
        sa.Column("data", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_chain_events_block_tx", "chain_events", ["block_number", "tx_hash"], unique=False)
    op.create_index("ix_chain_events_event_name", "chain_events", ["event_name"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_chain_events_event_name", table_name="chain_events")
    op.drop_index("ix_chain_events_block_tx", table_name="chain_events")
    op.drop_table("chain_events")
