from stravit_companion.identity import participant_id
from stravit_companion.parsing.leaderboard import LeaderboardItem, parse_leaderboard


def test_leaderboard_item_equality_reflects_all_fields():
    item_a = LeaderboardItem.from_raw_name(
        "Jane Doe",
        "test-identity-key",
        rank=1,
        distance=10.0,
        elevation=100,
        longest=5.0,
        count=1,
    )
    item_b = LeaderboardItem.from_raw_name(
        "Jane Doe",
        "test-identity-key",
        rank=1,
        distance=10.0,
        elevation=100,
        longest=5.0,
        count=1,
    )
    item_c = LeaderboardItem.from_raw_name(
        "Jane Doe",
        "test-identity-key",
        rank=1,
        distance=11.0,
        elevation=100,
        longest=5.0,
        count=1,
    )

    assert item_a == item_b
    assert item_a != item_c


def test_display_name_two_part_name_uses_initial():
    item = LeaderboardItem.from_raw_name(
        "Jane Doe",
        "test-identity-key",
        rank=1,
        distance=10.0,
        elevation=100,
        longest=5.0,
        count=1,
    )

    assert item.display_name == "Jane D."


def test_display_name_single_name_uses_first_syllable():
    item = LeaderboardItem.from_raw_name(
        "Zorro",
        "test-identity-key",
        rank=1,
        distance=10.0,
        elevation=100,
        longest=5.0,
        count=1,
    )

    assert item.display_name == "Zo"


def test_parse_leaderboard_pseudonymizes_source_names_and_skips_empty_rows():
    items = parse_leaderboard(
        "lp;nazwa;dystans;przewyzszenia;najdluzszy;suma\n"
        "1;  Jane   Doe ;10.5;100;5.0;2\n"
        ";ignored;0;0;0;0\n",
        "test-identity-key",
    )

    assert len(items) == 1
    assert items[0].participant_id == participant_id("Jane Doe", "test-identity-key")
    assert items[0].display_name == "Jane D."


def test_participant_id_depends_on_key_but_not_redundant_whitespace():
    assert participant_id("Jane Doe", "key-a") == participant_id(
        "  Jane   Doe ", "key-a"
    )
    assert participant_id("Jane Doe", "key-a") != participant_id("Jane Doe", "key-b")
    assert participant_id("Jane Doe", "key-a") != participant_id("Janet Doe", "key-a")
