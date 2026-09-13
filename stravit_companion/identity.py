"""Privacy-preserving participant identity helpers."""

import hashlib
import hmac


def normalize_name(name: str) -> str:
    """Trim and collapse whitespace without changing the participant's case."""
    return " ".join(name.split())


def participant_id(raw_name: str, identity_hash_key: str) -> str:
    """Return a deterministic, keyed identifier for a source participant name."""
    return hmac.new(
        identity_hash_key.encode("utf-8"),
        normalize_name(raw_name).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def abbreviate_name(raw_name: str) -> str:
    """Keep the existing alert/CLI abbreviation behaviour."""
    parts = normalize_name(raw_name).split()
    if len(parts) >= 2:
        return f"{parts[0]} {parts[1][0]}."
    word = parts[0]
    vowels = "aeiouyąęóAEIOUYĄĘÓ"
    syllable = ""
    for character in word:
        syllable += character
        if character in vowels and len(syllable) >= 2:
            break
    return syllable
