from stravit_companion.parsing.leaderboard import LeaderboardItem


def test_leaderboard_item_equality_reflects_all_fields():
    item_a = LeaderboardItem(
        name="Jane Doe",
        rank=1,
        distance=10.0,
        elevation=100,
        longest=5.0,
        count=1,
    )
    item_b = LeaderboardItem(
        name="Jane Doe",
        rank=1,
        distance=10.0,
        elevation=100,
        longest=5.0,
        count=1,
    )
    item_c = LeaderboardItem(
        name="Jane Doe",
        rank=1,
        distance=11.0,
        elevation=100,
        longest=5.0,
        count=1,
    )

    assert item_a == item_b
    assert item_a != item_c


def test_display_name_two_part_name_uses_initial():
    item = LeaderboardItem(
        name="Jane Doe",
        rank=1,
        distance=10.0,
        elevation=100,
        longest=5.0,
        count=1,
    )

    assert item.display_name == "Jane D."


def test_display_name_single_name_uses_first_syllable():
    item = LeaderboardItem(
        name="Zorro",
        rank=1,
        distance=10.0,
        elevation=100,
        longest=5.0,
        count=1,
    )

    assert item.display_name == "Zo"
