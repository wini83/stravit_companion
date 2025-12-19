from stravit_companion.alerts.detector import (
    build_alert_from_detected,
    detect_alerts,
    get_neighbors,
)


def test_get_neighbors_returns_me_ahead_behind(item_factory):
    items = [
        item_factory(name="Alice Example", rank=1, distance=15.0),
        item_factory(name="Jane Doe", rank=2, distance=13.0),
        item_factory(name="Bob Example", rank=3, distance=12.5),
        item_factory(name="Cara Example", rank=4, distance=12.0),
    ]

    me, ahead, behind = get_neighbors(items, "Jane Doe", window=2)

    assert me is not None
    assert me.rank == 2
    assert [a.rank for a in ahead] == [1]
    assert [b.rank for b in behind] == [3, 4]


def test_detect_alerts_rank_change_triggers_position_alert(item_factory):
    prev_items = [
        item_factory(name="Alice Example", rank=1, distance=15.0),
        item_factory(name="Jane Doe", rank=2, distance=13.0),
        item_factory(name="Bob Example", rank=3, distance=12.0),
    ]
    curr_items = [
        item_factory(name="Jane Doe", rank=1, distance=16.0),
        item_factory(name="Alice Example", rank=2, distance=15.5),
        item_factory(name="Bob Example", rank=3, distance=12.0),
    ]

    alerts = detect_alerts(prev_items, curr_items, "Jane Doe", window=1)

    assert any("Pozycja:" in a for a in alerts)


def test_detect_alerts_gap_changes_generate_neighbor_alerts(item_factory):
    prev_items = [
        item_factory(name="Alice Example", rank=1, distance=15.0),
        item_factory(name="Jane Doe", rank=2, distance=13.0),
        item_factory(name="Bob Example", rank=3, distance=12.0),
    ]
    curr_items = [
        item_factory(name="Alice Example", rank=1, distance=15.8),
        item_factory(name="Jane Doe", rank=2, distance=14.0),
        item_factory(name="Bob Example", rank=3, distance=12.5),
    ]

    alerts = detect_alerts(prev_items, curr_items, "Jane Doe", window=1)

    assert len(alerts) == 2
    assert any("Alice" in message for message in alerts)
    assert any("Bob" in message for message in alerts)


def test_build_alert_from_detected_returns_none_when_empty():
    assert build_alert_from_detected([]) is None


def test_build_alert_from_detected_builds_alert_with_message():
    alert = build_alert_from_detected(["one", "two"], title="Title", priority=1)

    assert alert is not None
    assert alert.title == "Title"
    assert alert.message == "one\ntwo"
    assert alert.priority == 1


def test_detect_alerts_returns_empty_when_user_missing(item_factory):
    prev_items = [item_factory(name="Alice Example", rank=1, distance=15.0)]
    curr_items = [item_factory(name="Alice Example", rank=1, distance=16.0)]

    alerts = detect_alerts(prev_items, curr_items, "Missing User", window=1)

    assert alerts == []
