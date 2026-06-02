"""Scrape song lyrics from Genius API grouped by mood label (semantic affect, not genre)."""

from __future__ import annotations

import argparse
import os
import time
import warnings
from pathlib import Path

import certifi
import lyricsgenius
from dotenv import load_dotenv

from scrapers.io_utils import load_from_json, save_records_to_csv, save_to_json
from scrapers.preprocess import deduplicate_songs, song_record

load_dotenv()

MOOD_ARTISTS: dict[str, list[str]] = {
    "sad": [
        "Adele",
        "Radiohead",
        "Lana Del Rey",
        "Billie Eilish",
    ],
    "happy": [
        "Pharrell Williams",
        "Katy Perry",
        "Bruno Mars",
        "Dua Lipa",
    ],
    "angry": [
        "Rage Against the Machine",
        "Slipknot",
        "System of a Down",
        "Korn",
    ],
    "neutral": [
        "Coldplay",
        "The Beatles",
        "Fleetwood Mac",
        "Pink Floyd",
    ],
    "club": [
        "David Guetta",
        "Calvin Harris",
        "Disclosure",
        "Fisher",
    ],
}

DEFAULT_MAX_SONGS_PER_ARTIST = 8
SLEEP_BETWEEN_ARTISTS_SEC = 2.5
RAW_DIR = Path("data/raw")
PROCESSED_CSV = Path("data/processed/songs.csv")
PROCESSED_JSON = Path("data/processed/songs.json")


def _ssl_verify() -> bool | str:
    """Return certifi bundle path, or False when verification is disabled in .env."""
    flag = os.getenv("GENIUS_VERIFY_SSL", "true").strip().lower()
    if flag in ("0", "false", "no"):
        return False
    bundle = certifi.where()
    os.environ.setdefault("SSL_CERT_FILE", bundle)
    os.environ.setdefault("REQUESTS_CA_BUNDLE", bundle)
    return bundle


def _configure_session(session) -> None:
    """Apply SSL settings to the lyricsgenius requests session."""
    verify = _ssl_verify()
    session.verify = verify
    if verify is False:
        try:
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        except ImportError:
            warnings.filterwarnings("ignore", message="Unverified HTTPS request")


def _get_genius() -> lyricsgenius.Genius:
    token = os.getenv("GENIUS_TOKEN")
    if not token:
        raise RuntimeError("GENIUS_TOKEN missing in .env")

    genius = lyricsgenius.Genius(
        token,
        timeout=20,
        remove_section_headers=False,
    )
    genius.skip_non_songs = True
    _configure_session(genius._session)
    return genius


def get_songs_by_mood(
    genius: lyricsgenius.Genius,
    mood: str,
    *,
    max_songs_per_artist: int = DEFAULT_MAX_SONGS_PER_ARTIST,
    language: str = "en",
) -> list[dict]:
    """Fetch songs for all artists mapped to a mood label."""
    if mood not in MOOD_ARTISTS:
        raise ValueError(f"Unknown mood: {mood}. Choose from {list(MOOD_ARTISTS)}")

    records: list[dict] = []
    for artist_name in MOOD_ARTISTS[mood]:
        artist = genius.search_artist(artist_name, max_songs=max_songs_per_artist)
        if artist is None:
            print(f"Warning: no results for artist {artist_name!r}")
            time.sleep(SLEEP_BETWEEN_ARTISTS_SEC)
            continue

        for song in artist.songs:
            if not song.lyrics:
                continue
            raw_id = song._body.get("id") if hasattr(song, "_body") else None
            song_id = f"genius-{raw_id}" if raw_id is not None else f"genius-{song.title}-{song.artist}"
            records.append(
                song_record(
                    song_id=song_id,
                    title=song.title,
                    artist=song.artist,
                    mood_label=mood,
                    lyrics=song.lyrics,
                    language=language,
                )
            )
        time.sleep(SLEEP_BETWEEN_ARTISTS_SEC)

    return deduplicate_songs(records)


def scrape_all_moods(
    output_dir: str | Path = RAW_DIR,
    *,
    max_songs_per_artist: int = DEFAULT_MAX_SONGS_PER_ARTIST,
    moods: list[str] | None = None,
) -> list[dict]:
    """Scrape moods, save per-mood JSON and combined processed CSV."""
    genius = _get_genius()
    output_dir = Path(output_dir)
    mood_list = moods if moods is not None else list(MOOD_ARTISTS)
    all_records: list[dict] = []

    for mood in mood_list:
        if mood not in MOOD_ARTISTS:
            raise ValueError(f"Unknown mood: {mood}")
        print(f"Scraping mood: {mood}")
        mood_records = get_songs_by_mood(
            genius,
            mood,
            max_songs_per_artist=max_songs_per_artist,
        )
        save_to_json(mood_records, output_dir / f"{mood}.json")
        all_records.extend(mood_records)
        print(f"  -> {len(mood_records)} songs")

    all_records = deduplicate_songs(all_records)
    save_records_to_csv(all_records, PROCESSED_CSV)
    save_to_json(all_records, PROCESSED_JSON)
    print(f"Total unique songs: {len(all_records)} -> {PROCESSED_CSV}")
    return all_records


def build_processed_from_raw(raw_dir: str | Path = RAW_DIR) -> list[dict]:
    """Merge per-mood raw JSON files into deduplicated processed CSV."""
    raw_dir = Path(raw_dir)
    all_records: list[dict] = []
    for mood in MOOD_ARTISTS:
        path = raw_dir / f"{mood}.json"
        if path.exists():
            all_records.extend(load_from_json(path))

    all_records = deduplicate_songs(all_records)
    save_records_to_csv(all_records, PROCESSED_CSV)
    save_to_json(all_records, PROCESSED_JSON)
    print(f"Rebuilt {len(all_records)} songs -> {PROCESSED_CSV}")
    return all_records


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape Genius lyrics by mood (semantic affect labels)."
    )
    parser.add_argument(
        "--max-songs-per-artist",
        type=int,
        default=DEFAULT_MAX_SONGS_PER_ARTIST,
        help="Max songs to fetch per artist (default: 8)",
    )
    parser.add_argument(
        "--from-raw",
        action="store_true",
        help="Rebuild processed CSV from existing data/raw/*.json",
    )
    parser.add_argument(
        "--mood",
        choices=list(MOOD_ARTISTS),
        help="Scrape only this mood (default: all five)",
    )
    args = parser.parse_args()

    if args.from_raw:
        build_processed_from_raw()
        return

    moods = [args.mood] if args.mood else None
    scrape_all_moods(
        max_songs_per_artist=args.max_songs_per_artist,
        moods=moods,
    )


if __name__ == "__main__":
    main()
