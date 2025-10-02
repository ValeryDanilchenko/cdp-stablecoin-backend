from datetime import datetime

from sqlalchemy import BigInteger, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Position(Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    position_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    owner_address: Mapped[str] = mapped_column(String(64), index=True)
    collateral_symbol: Mapped[str] = mapped_column(String(32))
    collateral_amount: Mapped[str] = mapped_column(String(64))  # decimal as string for demo
    debt_symbol: Mapped[str] = mapped_column(String(32))
    debt_amount: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (Index("ix_positions_owner", "owner_address"),)
