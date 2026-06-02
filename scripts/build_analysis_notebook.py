"""Regenerate the analysis notebook (English, DBSCAN, rich Plotly hovers)."""

import json
import sys
from pathlib import Path

NOTEBOOK_PATH = Path("notebooks/song_mood_analysis.ipynb")


def md(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "metadata": {},
        "source": source.splitlines(keepends=True),
        "outputs": [],
        "execution_count": None,
    }


CELLS = [
    md(
        """# Song Lyrics: Embeddings, 2D Manifold & Clustering (Lab 12)

Custom Genius lyrics dataset (`mood_label` as reference only). Pipeline:
1. Text embeddings (`sentence-transformers`)
2. **PCA** and **t-SNE** (side-by-side, interactive hovers)
3. `find_optimal_clusters` → choose **k**
4. **KMeans** (fixed **k**) and **DBSCAN** (data-driven cluster count)

Run all cells from the **repository root**."""
    ),
    code(
        """import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, davies_bouldin_score, adjusted_rand_score
from sklearn.neighbors import NearestNeighbors
from numpy.typing import NDArray

# Cursor/Jupyter often starts in notebooks/ — move to repo root
ROOT = Path.cwd()
if not (ROOT / "data" / "processed" / "songs.csv").exists():
    ROOT = ROOT.parent
os.chdir(ROOT)
print("Project root:", ROOT.resolve())"""
    ),
    md(
        """## Step 1: Text vectorization

Load `data/processed/songs.csv`, embed the `lyrics` column with `all-MiniLM-L6-v2`, save `embeddings.npy` and `labels.npy`."""
    ),
    code(
        """CSV_PATH = "data/processed/songs.csv"
EMBEDDINGS_PATH = "data/processed/embeddings.npy"
LABELS_PATH = "data/processed/labels.npy"
OUTPUTS_DIR = "outputs"

os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"Missing {CSV_PATH}. Run: python -m scrapers.genius_scraper")

print(f"Loading {CSV_PATH}...")
df = pd.read_csv(CSV_PATH)
required = {"title", "artist", "mood_label", "lyrics"}
missing = required - set(df.columns)
if missing:
    raise ValueError(f"CSV missing columns: {missing}")

print(f"Songs: {len(df)} | moods: {df['mood_label'].value_counts().to_dict()}")

model = SentenceTransformer("all-MiniLM-L6-v2")
lyrics_list = df["lyrics"].fillna("").astype(str).tolist()
embeddings = model.encode(lyrics_list, show_progress_bar=True)
print(f"Embeddings shape: {embeddings.shape}")

np.save(EMBEDDINGS_PATH, embeddings)
np.save(LABELS_PATH, df["mood_label"].to_numpy())
print(f"Saved {EMBEDDINGS_PATH} and {LABELS_PATH}")"""
    ),
    md(
        """## Step 2: PCA & t-SNE (2D)

Interactive Plotly charts: hover shows **song title**, **artist**, and **mood**. Static PNGs saved to `outputs/`."""
    ),
    code(
        '''def make_hover_frame(coords: np.ndarray, x_col: str, y_col: str) -> pd.DataFrame:
    """Build a dataframe for scatter plots with rich hover fields."""
    return pd.DataFrame(
        {
            x_col: coords[:, 0],
            y_col: coords[:, 1],
            "title": df["title"].astype(str).values,
            "artist": df["artist"].astype(str).values,
            "mood_label": df["mood_label"].astype(str).values,
        }
    )


def plot_2d_manifold(
    frame: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: str,
    title: str,
    png_name: str,
) -> go.Figure:
    fig = px.scatter(
        frame,
        x=x_col,
        y=y_col,
        color=color_col,
        hover_name="title",
        custom_data=["artist", "mood_label"],
        title=title,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_traces(
        marker=dict(size=10, opacity=0.85),
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Artist: %{customdata[0]}<br>"
            "Mood: %{customdata[1]}<br>"
            f"{x_col}: %{{x:.3f}}<br>"
            f"{y_col}: %{{y:.3f}}"
            "<extra></extra>"
        ),
    )
    fig.update_layout(template="plotly_white", legend_title_text=color_col.replace("_", " ").title())
    png_path = os.path.join(OUTPUTS_DIR, png_name)
    try:
        fig.write_image(png_path, scale=2)
        print(f"Saved {png_path}")
    except Exception as exc:
        print(f"PNG export skipped ({exc}). Install kaleido: pip install kaleido")
    return fig


print("PCA -> 2D...")
pca = PCA(n_components=2, random_state=42)
pca_coords = pca.fit_transform(embeddings)
print(f"Explained variance ratio: {pca.explained_variance_ratio_.sum():.3f}")

print("t-SNE -> 2D...")
tsne = TSNE(n_components=2, random_state=42, perplexity=30, init="pca", learning_rate="auto")
tsne_coords = tsne.fit_transform(embeddings)

df_pca = make_hover_frame(pca_coords, "PC1", "PC2")
df_tsne = make_hover_frame(tsne_coords, "TSNE1", "TSNE2")

fig_pca = plot_2d_manifold(df_pca, "PC1", "PC2", "mood_label", "PCA colored by mood (proxy label)", "pca_mood.png")
fig_tsne = plot_2d_manifold(df_tsne, "TSNE1", "TSNE2", "mood_label", "t-SNE colored by mood (proxy label)", "tsne_mood.png")

# Side-by-side interactive view
fig_both = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=("PCA", "t-SNE"),
    horizontal_spacing=0.08,
)
for fig_part, cols, prefix in [(fig_pca, ("PC1", "PC2"), "pca"), (fig_tsne, ("TSNE1", "TSNE2"), "tsne")]:
    for trace in fig_part.data:
        trace.showlegend = True
        fig_both.add_trace(trace, row=1, col=1 if prefix == "pca" else 2)
fig_both.update_layout(
    title="2D manifolds (hover: title, artist, mood)",
    template="plotly_white",
    height=520,
    width=1100,
)
fig_both.show()
fig_pca.show()
fig_tsne.show()'''
    ),
    md("## Step 3: Optimal cluster count (`find_optimal_clusters`)"),
    code(
        """def find_optimal_clusters(
    embeddings: NDArray,
    max_clusters: int = 15,
    random_state: int = 42,
) -> tuple[go.Figure, dict[str, int]]:
    max_clusters = min(max_clusters, len(embeddings) - 1)
    range_n_clusters = list(range(2, max_clusters + 1))

    inertia_values = []
    silhouette_values = []
    davies_bouldin_values = []

    for n_clusters in range_n_clusters:
        kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings)
        inertia_values.append(kmeans.inertia_)
        if len(np.unique(cluster_labels)) > 1:
            silhouette_values.append(silhouette_score(embeddings, cluster_labels))
        else:
            silhouette_values.append(0.0)
        davies_bouldin_values.append(davies_bouldin_score(embeddings, cluster_labels))

    optimal_k = {
        "elbow": range_n_clusters[int(np.argmin(np.diff(np.diff(inertia_values))) + 1)]
        if len(inertia_values) >= 3
        else range_n_clusters[0],
        "silhouette": range_n_clusters[int(np.argmax(silhouette_values))],
        "davies_bouldin": range_n_clusters[int(np.argmin(davies_bouldin_values))],
    }

    fig = make_subplots(
        rows=3,
        cols=1,
        subplot_titles=(
            "Elbow (inertia)",
            "Silhouette (higher is better)",
            "Davies–Bouldin (lower is better)",
        ),
        vertical_spacing=0.12,
    )
    fig.add_trace(
        go.Scatter(x=range_n_clusters, y=inertia_values, mode="lines+markers", name="Inertia"),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=range_n_clusters, y=silhouette_values, mode="lines+markers", name="Silhouette"),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=range_n_clusters, y=davies_bouldin_values, mode="lines+markers", name="Davies–Bouldin"),
        row=3,
        col=1,
    )
    fig.update_layout(title="Choosing k for KMeans", height=800, width=900, template="plotly_white")
    return fig, optimal_k


mood_labels = np.load(LABELS_PATH, allow_pickle=True)
TRUE_K = len(np.unique(mood_labels))
print(f"Unique mood labels in dataset: {TRUE_K}")

fig_optimal, optimal_k = find_optimal_clusters(embeddings, max_clusters=15)
fig_optimal.show()
print("Suggested k:", optimal_k)

KMEANS_K = optimal_k["silhouette"]
print(f"Using k={KMEANS_K} for KMeans (silhouette pick)")"""
    ),
    md(
        """## Step 4: Clustering - KMeans (fixed k) and DBSCAN (automatic k)

- **KMeans**: `k` from step 3 (or set `KMEANS_K = 5` to match five moods).
- **DBSCAN**: `eps` from the k-distance elbow; number of clusters is **not** fixed upfront.
- Interactive plots: color = cluster assignment; hover = **title + artist + mood**."""
    ),
    code(
        '''def cluster_embeddings(embeddings: NDArray, algorithm: str, **kwargs) -> tuple[np.ndarray, object]:
    if algorithm == "KMeans":
        model = KMeans(**kwargs)
        labels = model.fit_predict(embeddings)
    elif algorithm == "GaussianMixture":
        model = GaussianMixture(**kwargs)
        labels = model.predict(model.fit(embeddings))
    elif algorithm == "AgglomerativeClustering":
        model = AgglomerativeClustering(**kwargs)
        labels = model.fit_predict(embeddings)
    elif algorithm == "DBSCAN":
        model = DBSCAN(**kwargs)
        labels = model.fit_predict(embeddings)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    return labels, model


def suggest_dbscan_eps(embeddings: NDArray, k: int = 5) -> float:
    """k-distance plot helper; returns a reasonable eps (90th percentile knee)."""
    nbrs = NearestNeighbors(n_neighbors=k, metric="cosine").fit(embeddings)
    distances, _ = nbrs.kneighbors(embeddings)
    k_dist = np.sort(distances[:, -1])
    eps = float(np.percentile(k_dist, 90))
    fig = px.line(x=np.arange(len(k_dist)), y=k_dist, title=f"{k}-NN distance (cosine) for DBSCAN eps")
    fig.add_vline(x=len(k_dist) * 0.9, line_dash="dash", annotation_text=f"suggested eps={eps:.3f}")
    fig.update_layout(xaxis_title="Points (sorted)", yaxis_title="Distance", template="plotly_white")
    fig.show()
    return eps


def plot_clusters_interactive(
    coords: np.ndarray,
    cluster_labels: np.ndarray,
    x_col: str,
    y_col: str,
    title: str,
    png_name: str | None = None,
) -> go.Figure:
    frame = make_hover_frame(coords, x_col, y_col)
    frame["cluster"] = cluster_labels.astype(str)

    fig = px.scatter(
        frame,
        x=x_col,
        y=y_col,
        color="cluster",
        hover_name="title",
        custom_data=["artist", "mood_label", "cluster"],
        title=title,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_traces(
        marker=dict(size=10, opacity=0.85),
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Artist: %{customdata[0]}<br>"
            "Mood: %{customdata[1]}<br>"
            "Cluster: %{customdata[2]}<br>"
            f"{x_col}: %{{x:.3f}}<br>"
            f"{y_col}: %{{y:.3f}}"
            "<extra></extra>"
        ),
    )
    fig.update_layout(template="plotly_white", legend_title_text="Cluster")
    if png_name:
        try:
            fig.write_image(os.path.join(OUTPUTS_DIR, png_name), scale=2)
        except Exception:
            pass
    fig.show()
    return fig


# Reuse t-SNE 2D layout for clustering visuals (clearer separation than PCA for lyrics)
viz_coords = tsne_coords
VIZ_X, VIZ_Y = "TSNE1", "TSNE2"

# --- KMeans (k must be specified) ---
labels_kmeans, _ = cluster_embeddings(
    embeddings,
    "KMeans",
    n_clusters=KMEANS_K,
    random_state=42,
    n_init=10,
)
ari_kmeans = adjusted_rand_score(mood_labels, labels_kmeans)

# --- DBSCAN (k from data) ---
dbscan_eps = suggest_dbscan_eps(embeddings, k=5)
labels_dbscan, dbscan_model = cluster_embeddings(
    embeddings,
    "DBSCAN",
    eps=dbscan_eps,
    min_samples=5,
    metric="cosine",
)
n_dbscan_clusters = len(set(labels_dbscan)) - (1 if -1 in labels_dbscan else 0)
n_noise = int(np.sum(labels_dbscan == -1))
ari_dbscan = adjusted_rand_score(mood_labels, labels_dbscan) if n_dbscan_clusters > 1 else float("nan")

print("\n--- Adjusted Rand Index vs mood_label (proxy) ---")
print(f"KMeans (k={KMEANS_K}) ARI: {ari_kmeans:.4f}")
print(f"DBSCAN (eps={dbscan_eps:.3f}, clusters={n_dbscan_clusters}, noise={n_noise}) ARI: {ari_dbscan:.4f}")

plot_clusters_interactive(
    viz_coords,
    labels_kmeans,
    VIZ_X,
    VIZ_Y,
    f"KMeans (k={KMEANS_K}) on t-SNE - hover: song and artist",
    "kmeans_clusters_tsne.png",
)
plot_clusters_interactive(
    viz_coords,
    labels_dbscan,
    VIZ_X,
    VIZ_Y,
    f"DBSCAN on t-SNE - hover: song and artist",
    "dbscan_clusters_tsne.png",
)

# Optional: true mood coloring on same layout (sanity check for semantics)
plot_2d_manifold(
    make_hover_frame(viz_coords, VIZ_X, VIZ_Y),
    VIZ_X,
    VIZ_Y,
    "mood_label",
    "t-SNE colored by true mood (reference)",
    "tsne_mood_reference.png",
)'''
    ),
]

_py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python (SamePain DM)",
            "language": "python",
            "name": "samepain-dm",
        },
        "language_info": {
            "name": "python",
            "version": _py_version,
            "mimetype": "text/x-python",
            "codemirror_mode": {"name": "ipython", "version": 3},
            "pygments_lexer": "ipython3",
            "nbconvert_exporter": "python",
            "file_extension": ".py",
        },
    },
    "cells": CELLS,
}

NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
NOTEBOOK_PATH.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"Wrote {NOTEBOOK_PATH} ({len(CELLS)} cells)")
