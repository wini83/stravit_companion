import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ROOT_DIR = Path(__file__).resolve().parents[1]

# Ensure required settings are present before importing app modules.
os.environ.setdefault("DB_PATH", str(ROOT_DIR / "data" / "test.db"))
os.environ.setdefault("STRAVIT_BASE_URL", "https://example.invalid")
os.environ.setdefault("STRAVIT_EMAIL", "test@example.invalid")
os.environ.setdefault("STRAVIT_PASSWORD", "not-a-real-password")
os.environ.setdefault("STRAVIT_CSV_LINK", "challenge/example/export/leaderboard/csv")
os.environ.setdefault("MY_NAME", "Jane Doe")
os.environ.setdefault("PUSHOVER_USER", "u123")
os.environ.setdefault("PUSHOVER_TOKEN", "t123")


@pytest.fixture()
def item_factory():
    from stravit_companion.parsing.leaderboard import LeaderboardItem

    def _make(
        name: str = "Jane Doe",
        rank: int = 1,
        distance: float = 10.0,
        elevation: int = 100,
        longest: float = 5.0,
        count: int = 1,
    ) -> LeaderboardItem:
        return LeaderboardItem(
            name=name,
            rank=rank,
            distance=distance,
            elevation=elevation,
            longest=longest,
            count=count,
        )

    return _make


@pytest.fixture()
def sqlite_engine(tmp_path):
    from stravit_companion.db.base import Base

    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture()
def session_factory(sqlite_engine):
    return sessionmaker(bind=sqlite_engine, expire_on_commit=False, future=True)


@pytest.fixture()
def db_session(session_factory):
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
