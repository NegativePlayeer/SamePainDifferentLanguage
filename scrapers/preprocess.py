"""Lyrics cleaning and dataset deduplication."""

import re

SECTION_HEADER_RE = re.compile(
    r"\[\d*\s*(Verse|Chorus|Bridge|Intro|Outro|Hook|Refrain|Pre-Chorus).*?\]",
    re.I,
)
BRACKET_TAG_RE = re.compile(r"\[.*?\]")
TITLE_ARTIST_PREFIX_RE = re.compile(
    r"^\d+\s+Contributors.*?Lyrics\s*",
    re.I | re.DOTALL,
)


def clean_lyrics(lyrics: str) -> str:
    """Remove Genius section tags and contributor headers from lyrics text."""
    if not lyrics:
        return ""
    text = TITLE_ARTIST_PREFIX_RE.sub("", lyrics)
    text = BRACKET_TAG_RE.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def deduplicate_songs(records: list[dict]) -> list[dict]:
    """Keep first occurrence per (title, artist) pair (case-insensitive)."""
    seen: set[tuple[str, str]] = set()
    unique: list[dict] = []
    for record in records:
        key = (
            record.get("title", "").strip().lower(),
            record.get("artist", "").strip().lower(),
        )
        if not key[0] or key in seen:
            continue
        seen.add(key)
        unique.append(record)
    return unique


def song_record(
    *,
    song_id: str,
    title: str,
    artist: str,
    mood_label: str,
    lyrics: str,
    language: str = "en",
) -> dict:
    """Build a normalized song record dict for embedding and clustering."""
    cleaned = clean_lyrics(lyrics)
    return {
        "id": song_id,
        "title": title.strip(),
        "artist": artist.strip(),
        "mood_label": mood_label,
        "language": language,
        "lyrics": cleaned,
    }
