import pytest

from scripts.extract_release_notes import extract_release_notes

CHANGELOG = """\
# Changelog

## Unreleased

## v0.5.1 (2026-09-27)

### Fix

- repair publishing

## v0.5.0 (2026-09-15)

- previous release
"""


def test_extract_release_notes_returns_only_requested_section() -> None:
    assert extract_release_notes(CHANGELOG, "v0.5.1") == (
        "### Fix\n\n- repair publishing\n"
    )


def test_extract_release_notes_rejects_missing_release() -> None:
    with pytest.raises(ValueError, match=r"No changelog section found for v9\.9\.9"):
        extract_release_notes(CHANGELOG, "v9.9.9")
