from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from stravit_companion.db.base import Base


class LeaderboardSnapshot(Base):
    __tablename__ = "leaderboard_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # SNAPSHOT ID (wspólny dla jednego runa)
    ts: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)

    # IDENTYFIKATOR ZAWODNIKA
    name: Mapped[str] = mapped_column(String, nullable=False)

    # 👇 DANE
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    distance: Mapped[float] = mapped_column(Float, nullable=False)
    elevation: Mapped[int] = mapped_column(Integer, nullable=False)
    longest: Mapped[float] = mapped_column(Float, nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        Index("ix_snapshot_name", "ts", "name"),
        UniqueConstraint("ts", "name", name="uq_snapshot_name"),
    )
