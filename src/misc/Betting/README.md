# Marathonbet sumo odds downloader

`download_sumo_odds.py` reads the current Marathonbet sumo fixtures, follows
each event link, and saves the visible odds as JSON. Events sharing the same
start time are grouped into a file such as `odds/2026-11-12_05-00.json`.

Install the Python dependency:

```powershell
python -m pip install -r requirements.txt
```

Chrome is used by default. Run the downloader with:

```powershell
python download_sumo_odds.py
```

The command prints a timestamped message for every attempt. If no events are
available, or a transient Playwright error prevents an acquisition, it waits
30 minutes and tries again. It exits after the first odds file is successfully
written; press `Ctrl+C` to stop it while it is waiting.

Useful options:

```powershell
python download_sumo_odds.py --headed
python download_sumo_odds.py --browser-channel msedge
python download_sumo_odds.py --output-dir odds
python download_sumo_odds.py --retry-minutes 10
python download_sumo_odds.py --once
```

`--once` preserves one-shot behaviour: an empty listing exits with status 1
after reporting that no odds file was written. An empty listing does not
produce a Playwright timeout traceback.

If neither Chrome nor Edge is installed, install Playwright's browser once:

```powershell
python -m playwright install chromium
```

The page and prices can change at any time. The script only reads public
pre-match data; it does not log in or place bets.
