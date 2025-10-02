from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251002_0002"
down_revision = "20251002_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "risk_snapshots",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("position_id", sa.String(length=128), nullable=False),
        sa.Column("health_factor", sa.Float(), nullable=False),
        sa.Column("eligible", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_risk_snapshots_position", "risk_snapshots", ["position_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_risk_snapshots_position", table_name="risk_snapshots")
    op.drop_table("risk_snapshots")
