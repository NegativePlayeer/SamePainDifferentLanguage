# Run the analysis notebook from terminal (if Cursor kernel picker is stuck).
# Usage: .\scripts\run_notebook.ps1

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "Project root: $Root"
Write-Host "Using: $(python -c 'import sys; print(sys.executable)')"

python -m jupyter nbconvert `
    --to notebook `
    --execute "notebooks/song_mood_analysis.ipynb" `
    --output "song_mood_analysis_executed.ipynb" `
    --ExecutePreprocessor.timeout=600

if ($LASTEXITCODE -eq 0) {
    Write-Host "Done. Output: notebooks/song_mood_analysis_executed.ipynb"
} else {
    Write-Host "Failed. Install: pip install jupyter nbconvert ipykernel"
}
