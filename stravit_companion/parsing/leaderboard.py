import csv
from dataclasses import dataclass
from io import StringIO

from stravit_companion.identity import abbreviate_name, participant_id


@dataclass(frozen=True)
class LeaderboardItem:
    participant_id: str
    display_name: str
    rank: int
    distance: float
    elevation: int
    longest: float
    count: int

    @classmethod
    def from_raw_name(
        cls, raw_name: str, identity_hash_key: str, **statistics: int | float
    ) -> "LeaderboardItem":
        return cls(
            participant_id=participant_id(raw_name, identity_hash_key),
            display_name=abbreviate_name(raw_name),
            **statistics,
        )


def parse_leaderboard(csv_text: str, identity_hash_key: str) -> list[LeaderboardItem]:
    items: list[LeaderboardItem] = []

    reader = csv.DictReader(
        StringIO(csv_text),
        delimiter=";",
        skipinitialspace=True,
    )

    for row in reader:
        lp = (row.get("lp") or "").strip()
        if not lp:
            continue  # ostatnia linia / śmieci / partial row

        item = LeaderboardItem.from_raw_name(
            row["nazwa"],
            identity_hash_key,
            rank=int(lp),
            distance=float(row["dystans"]),
            elevation=int(row["przewyzszenia"]),
            longest=float(row["najdluzszy"]),
            count=int(row["suma"]),
        )
        items.append(item)

    return items
