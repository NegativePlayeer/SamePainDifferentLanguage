@echo off
cd /d "%~dp0"
echo Opening notebook in your browser (kernel works there)...
python -m jupyter notebook notebooks\song_mood_analysis.ipynb
pause
