# Scorito Ranking Dashboard

Small internal Streamlit dashboard for a Scorito ranking JSON API.

## What it does

- Fetches all ranking pages from the Scorito JSON endpoint.
- Stops when all participants are collected or when an empty ranking page is returned.
- Shows participant count, highest total points, and highest round points.
- Displays a searchable ranking table sorted by rank.
- Includes a refresh button and a last-updated timestamp.
- Shows a round leader visual for the current number 1 when a matching photo exists in `photos/`.

## Run on Windows

Open PowerShell in this folder and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation scripts, run this once for the current terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Streamlit will print a local URL, usually:

```text
http://localhost:8501
```

## Notes

The app uses the JSON API directly. It does not scrape HTML and does not require cookies, usernames, or passwords.

To show participant photos, add image files to the `photos` folder. Use the Scorito `UserName` as the filename, such as `HHBrons.jpg`.
