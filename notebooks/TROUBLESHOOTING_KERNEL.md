# Notebook kernel stuck on "Detecting kernels"

## Quick fix (Cursor / VS Code)

1. **Close** the notebook tab.
2. `Ctrl+Shift+P` → **Python: Select Interpreter** → choose  
   `C:\Users\dawid\miniconda3\python.exe`
3. `Ctrl+Shift+P` → **Developer: Reload Window**
4. Open `notebooks/song_mood_analysis.ipynb`
5. **Select Kernel** → pick **Python (SamePain DM)** (not "Detecting…" forever)

## If the list is still empty

In terminal (project root):

```powershell
pip install ipykernel jupyter
python -m ipykernel install --user --name samepain-dm --display-name "Python (SamePain DM)"
```

## Run without the GUI kernel picker

```powershell
.\scripts\run_notebook.ps1
```

This executes the notebook and saves `notebooks/song_mood_analysis_executed.ipynb`.

## OneDrive

If detection never finishes, copy the project to a local folder (e.g. `C:\dev\SamePainDifferentLanguage`) and open that folder in Cursor.
