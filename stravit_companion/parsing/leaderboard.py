import csv
from dataclasses import dataclass
from io import StringIO


@dataclass(frozen=True)
class LeaderboardItem:
    name: str
    rank: int
    distance: float
    elevation: int
    longest: float
    count: int

    @property
    def display_name(self) -> str:
        parts = self.name.strip().split()

        # 1️⃣ Imię + nazwisko
        if len(parts) >= 2:
            first_name = parts[0]
            last_name = parts[1]
            return f"{first_name} {last_name[0]}."

        # 2️⃣ Jednoczłonowe - heurystyka "pierwsza sylaba"
        return self._first_syllable(parts[0])

    @staticmethod
    def _first_syllable(word: str) -> str:
        """
        Bardzo prosta heurystyka:
        - bierzemy znaki do pierwszej samogłoski włącznie
        - minimum 2 znaki
        """
        vowels = "aeiouyąęóAEIOUYĄĘÓ"
        syllable = ""

        for ch in word:
            syllable += ch
            if ch in vowels and len(syllable) >= 2:
                break

        return syllable


def parse_leaderboard(csv_text: str) -> list[LeaderboardItem]:
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

        item = LeaderboardItem(
            rank=int(lp),
            name=row["nazwa"].strip(),
            distance=float(row["dystans"]),
            elevation=int(row["przewyzszenia"]),
            longest=float(row["najdluzszy"]),
            count=int(row["suma"]),
        )
        items.append(item)

    return items
