"""Open the analysis notebook in the browser — no Cursor kernel needed."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
notebook = ROOT / "notebooks" / "song_mood_analysis.ipynb"

print("Opening in browser:", notebook)
print("In the browser: Kernel -^> Python 3 / SamePain DM, then Run -^> Run All Cells")
subprocess.run(
    [sys.executable, "-m", "jupyter", "notebook", str(notebook)],
    cwd=ROOT,
)
