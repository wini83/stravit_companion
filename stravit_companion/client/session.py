import re

import requests
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_fixed

from stravit_companion.config import settings


class StravitFetchError(RuntimeError): ...


class StravitAuthError(RuntimeError): ...


class StravitSession:
    def __init__(self):
        self.session = requests.Session()

    def _get_csrf(self) -> str:
        logger.debug("Fetching CSRF token...")
        r = self.session.get(f"{settings.stravit_base_url}/login", timeout=10)
        r.raise_for_status()

        m = re.search(r'name="_csrf_token"\s+value="([^"]+)"', r.text)
        if not m:
            raise StravitAuthError("CSRF token not found")
        logger.debug("CSRF token found")
        return m.group(1)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def login(self) -> None:
        csrf = self._get_csrf()

        r = self.session.post(
            f"{settings.stravit_base_url}/login",
            data={
                "email": settings.stravit_email,
                "password": settings.stravit_password,
                "_csrf_token": csrf,
            },
            headers={"Referer": f"{settings.stravit_base_url}/login"},
            timeout=10,
        )
        r.raise_for_status()
        logger.debug(f"STATUS: {r.status_code}")
        logger.debug(f"HEADERS:{r.headers}")
        logger.debug(f"BODY:{r.text[:100]}")
        # with open("login_response.html", "w", encoding="utf-8") as f:
        #     f.write(r.text)

    def fetch_csv(self) -> str:
        r = self.session.get(
            f"{settings.stravit_base_url}/{settings.stravit_csv_link}",
            timeout=10,
        )
        r.raise_for_status()
        r.encoding = "utf-8"
        if not r.text.strip():
            raise StravitFetchError("CSV response is empty")
        return r.text
