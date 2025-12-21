import pytest

from stravit_companion.client import fetcher
from stravit_companion.client.fetcher import fetch_leaderboard_safe
from stravit_companion.client.session import (
    StravitAuthError,
    StravitFetchError,
)
from stravit_companion.parsing.leaderboard import LeaderboardItem


def test_fetch_leaderboard_happy_path(monkeypatch):
    fake_rows = [
        LeaderboardItem(
            rank=1,
            name="Alice Example",
            distance=10.0,
            elevation=100,
            longest=5.0,
            count=3,
        )
    ]

    class FakeSession:
        def login(self): ...
        def fetch_csv(self) -> str:
            return "csv content"

    monkeypatch.setattr(fetcher, "StravitSession", FakeSession)
    monkeypatch.setattr(fetcher, "parse_leaderboard", lambda _: fake_rows)

    rows = fetch_leaderboard_safe()

    assert rows == fake_rows


def test_fetch_leaderboard_auth_error(monkeypatch):
    class FakeSession:
        def login(self):
            raise StravitAuthError("auth failed")

    monkeypatch.setattr(fetcher, "StravitSession", FakeSession)

    rows = fetch_leaderboard_safe()

    assert rows == []


def test_fetch_leaderboard_fetch_error(monkeypatch):
    class FakeSession:
        def login(self): ...
        def fetch_csv(self):
            raise StravitFetchError("csv down")

    monkeypatch.setattr(fetcher, "StravitSession", FakeSession)

    rows = fetch_leaderboard_safe()

    assert rows == []


def test_fetch_leaderboard_parse_error(monkeypatch):
    class FakeSession:
        def login(self): ...
        def fetch_csv(self):
            return "broken csv"

    def boom(_: str):
        raise ValueError("csv garbage")

    monkeypatch.setattr(fetcher, "StravitSession", FakeSession)
    monkeypatch.setattr(fetcher, "parse_leaderboard", boom)

    rows = fetch_leaderboard_safe()

    assert rows == []


def test_fetch_leaderboard_unexpected_error(monkeypatch):
    class FakeSession:
        def login(self):
            raise RuntimeError("segfault of the mind")

    monkeypatch.setattr(fetcher, "StravitSession", FakeSession)

    with pytest.raises(RuntimeError):
        fetch_leaderboard_safe()
