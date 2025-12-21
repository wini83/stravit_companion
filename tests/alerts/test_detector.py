from stravit_companion.alerts.detector import detect_alert_events
from stravit_companion.alerts.models import AlertKind
from stravit_companion.parsing.leaderboard import LeaderboardItem


def item(
    name: str,
    rank: int,
    distance: float,
) -> LeaderboardItem:
    return LeaderboardItem(
        name=name,
        rank=rank,
        distance=distance,
        elevation=0,
        longest=0,
        count=0,
    )


def test_no_me_in_snapshot_returns_no_events():
    prev = [item("Alice", 1, 100)]
    curr = [item("Alice", 1, 101)]

    events = detect_alert_events(prev, curr, my_name="Me")

    assert events == []


def test_position_change_also_emits_gap_status_events():
    prev = [
        item("Alice", 1, 110),
        item("Me", 2, 100),
        item("Bob", 3, 95),
    ]
    curr = [
        item("Me", 1, 120),
        item("Alice", 2, 110),
        item("Bob", 3, 98),
    ]

    events = detect_alert_events(prev, curr, my_name="Me", window=1)

    # 1️⃣ zmiana pozycji MUSI być
    pos_events = [e for e in events if e.kind == AlertKind.POSITION_CHANGE]
    assert len(pos_events) == 1
    assert pos_events[0].prev_value == 2
    assert pos_events[0].curr_value == 1

    # 2️⃣ gapy MUSZĄ być policzone dla nowego okna
    gap_events = [e for e in events if e.kind == AlertKind.GAP_STATUS]
    assert len(gap_events) >= 1

    # 3️⃣ Alice jest teraz w oknie
    alice = next(e for e in gap_events if e.name == "Alice")
    assert alice.curr_value == -10  # 110 - 120


def test_gap_status_for_existing_rival():
    prev = [
        item("Alice", 1, 110),
        item("Me", 2, 100),
        item("Bob", 3, 95),
    ]
    curr = [
        item("Alice", 1, 112),
        item("Me", 2, 105),
        item("Bob", 3, 97),
    ]

    events = detect_alert_events(prev, curr, my_name="Me", window=1)

    gap_events = [e for e in events if e.kind == AlertKind.GAP_STATUS]
    assert len(gap_events) == 2

    alice = next(e for e in gap_events if e.name == "Alice")
    bob = next(e for e in gap_events if e.name == "Bob")

    assert alice.prev_value == 10  # 110 - 100
    assert alice.curr_value == 7  # 112 - 105

    assert bob.prev_value == -5  # 95 - 100
    assert bob.curr_value == -8  # 97 - 105


def test_new_rival_in_window_has_no_prev_gap():
    prev = [
        item("Alice", 1, 110),
        item("Me", 2, 100),
        item("Charlie", 3, 80),
    ]
    curr = [
        item("Alice", 1, 110),
        item("Bob", 2, 102),
        item("Me", 3, 100),
    ]

    events = detect_alert_events(prev, curr, my_name="Me", window=1)

    gap_events = [e for e in events if e.kind == AlertKind.GAP_STATUS]
    bob = next(e for e in gap_events if e.name == "Bob")

    assert bob.prev_value is None
    assert bob.curr_value == 2  # 102 - 100


def test_no_changes_produces_no_events():
    prev = [
        item("Alice", 1, 110),
        item("Me", 2, 100),
    ]
    curr = [
        item("Alice", 1, 110),
        item("Me", 2, 100),
    ]

    events = detect_alert_events(prev, curr, my_name="Me")

    assert events == []
