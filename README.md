# SamePainDifferentLanguage

Custom dataset of song lyrics (Genius API) labeled by **mood** (`mood_label`), for semantic clustering — whether sad texts group with sad, happy with happy, etc. (not by musical genre).

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` (scraping only):

```
GENIUS_TOKEN=your_token_here
```

### SSL on Windows (CERTIFICATE_VERIFY_FAILED)

```bash
pip install -U certifi
```

If it still fails, add to `.env` (local dev only):

```
GENIUS_VERIFY_SSL=false
```

## Project layout (after merge)

```
scrapers/              # Genius mood scraper + preprocess
data/processed/
  songs.csv            # 160 songs, columns: id, title, artist, mood_label, language, lyrics
  embeddings.npy       # (160, 384) — sentence-transformers
  labels.npy           # mood_label per row (for coloring plots)
  analiza_utworow_i_pca.ipynb   # Tasks 1–4: embed, PCA, t-SNE, clustering
outputs/
  pca_mood.png
  tsne_mood.png
data/raw/              # per-mood JSON (gitignored)
```

**Run the notebook from the repository root** so paths like `data/processed/songs.csv` resolve correctly.

## 1. Scrape lyrics (optional if `songs.csv` already present)

```bash
python -m scrapers.genius_scraper
python -m scrapers.genius_scraper --from-raw   # rebuild CSV from data/raw/*.json
```

## 2. Analysis (ziomki — notebook)

Open `data/processed/analiza_utworow_i_pca.ipynb` and run all cells, or re-run to refresh artifacts:

- Embeddings: `all-MiniLM-L6-v2` on column `lyrics`
- Side-by-side **PCA** and **t-SNE** (color = `mood_label`)
- `find_optimal_clusters` → **KMeans** (+ GMM in notebook)
- Figures saved to `outputs/`

## Mood labels (proxy ground truth)

| `mood_label` | Example artists |
|--------------|-----------------|
| sad | Adele, Radiohead, Lana Del Rey, Billie Eilish |
| happy | Pharrell Williams, Katy Perry, Bruno Mars, Dua Lipa |
| angry | RATM, Slipknot, System of a Down, Korn |
| neutral | Coldplay, The Beatles, Fleetwood Mac, Pink Floyd |
| club | David Guetta, Calvin Harris, Disclosure, Fisher |

## Git branches (merged into `master`)

- `feature-tasks-1-2` — notebook, embeddings, PCA/t-SNE
- `feature-tasks-3-4` — clustering, plotly, evaluation (ARI)

`pubmed_scraper` was removed from the project; Genius pipeline does not use it.
