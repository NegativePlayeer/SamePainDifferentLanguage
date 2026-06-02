# SamePainDifferentLanguage

Custom dataset of song lyrics (Genius API) labeled by **mood** (`mood_label`), for semantic clustering — whether sad texts group with sad, happy with happy, etc. (not by musical genre).

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env`:

```
GENIUS_TOKEN=your_token_here
```

### SSL on Windows (CERTIFICATE_VERIFY_FAILED)

The scraper uses the `certifi` CA bundle by default. If it still fails (common with Miniconda):

```bash
pip install -U certifi
python -m scrapers.genius_scraper
```

Last resort — add to `.env` (disables HTTPS verification, local dev only):

```
GENIUS_VERIFY_SSL=false
```

## Scrape lyrics by mood

Full scrape (5 moods × 4 artists × 8 songs ≈ 100+ unique tracks after dedup):

```bash
python -m scrapers.genius_scraper
```

One mood only (smoke test):

```bash
python -m scrapers.genius_scraper --mood sad --max-songs-per-artist 2
```

Rebuild `data/processed/songs.csv` from cached raw JSON:

```bash
python -m scrapers.genius_scraper --from-raw
```

Outputs:

- `data/raw/{sad,happy,angry,neutral,club}.json` — per-mood records (gitignored)
- `data/processed/songs.csv` — columns: `id`, `title`, `artist`, `mood_label`, `language`, `lyrics`

## Mood labels (proxy ground truth)

| `mood_label` | Example artists |
|--------------|-----------------|
| sad | Adele, Radiohead, Lana Del Rey, Billie Eilish |
| happy | Pharrell Williams, Katy Perry, Bruno Mars, Dua Lipa |
| angry | RATM, Slipknot, System of a Down, Korn |
| neutral | Coldplay, The Beatles, Fleetwood Mac, Pink Floyd |
| club | David Guetta, Calvin Harris, Disclosure, Fisher |

## Next step (Lab 12)

Embed `lyrics` with sentence-transformers, then PCA / t-SNE and clustering (KMeans + DBSCAN), coloring points by `mood_label`.
