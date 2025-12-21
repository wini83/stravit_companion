from loguru import logger

from stravit_companion.client.session import (
    StravitAuthError,
    StravitFetchError,
    StravitSession,
)
from stravit_companion.parsing.leaderboard import LeaderboardItem, parse_leaderboard


class StravitParseError(RuntimeError): ...


def fetch_leaderboard_safe() -> list[LeaderboardItem]:
    logger.info("Fetching new data from Stravit")

    try:
        client = StravitSession()
        client.login()

        csv_text = client.fetch_csv()

        try:
            rows = parse_leaderboard(csv_text)
        except Exception as e:
            raise StravitParseError("Failed to parse leaderboard CSV") from e

        if not rows:
            logger.warning("Leaderboard fetched but empty")

        return rows

    except (StravitAuthError, StravitFetchError) as e:
        logger.error(f"Stravit unavailable: {e}")
        return []

    except StravitParseError:
        logger.error("Failed to parse leaderboard CSV")
        return []

    except Exception:
        # BUG / regression → ma wybuchnąć
        logger.critical("Unexpected Stravit failure", exc_info=True)
        raise
