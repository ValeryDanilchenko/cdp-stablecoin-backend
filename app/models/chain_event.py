from datetime import datetime

from sqlalchemy import BigInteger, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ChainEvent(Base):
    __tablename__ = "chain_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    block_number: Mapped[int] = mapped_column(Integer, index=True)
    tx_hash: Mapped[str] = mapped_column(String(80), index=True)
    log_index: Mapped[int] = mapped_column(Integer)
    event_name: Mapped[str] = mapped_column(String(64), index=True)
    contract_address: Mapped[str] = mapped_column(String(64), index=True)
    data: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    __table_args__ = (
        Index("ix_chain_events_block_tx", "block_number", "tx_hash"),
    )
