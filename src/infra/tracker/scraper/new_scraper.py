"Downloads 'current standings' (end of basho pages) with max info."""

import os
import time
import requests

def get_months(year):
    """Generates the list of months based on the year constraints."""
    if year == 2026:
        return [1, 3, 5]
    return range(1, 13, 2)

def download_banzuke():
    base_url = "https://sumodb.sumogames.de/Banzuke.aspx"
    output_dir = "files/output/scraper2"
    os.makedirs(output_dir, exist_ok=True)
    
    pending = []
    years = range(1958, 2027)

    # Initial population of the pending list
    for year in years:
        for month in get_months(year):
            pending.append((year, month))

    while pending:
        next_round = []
        for year, month in pending:
            filename = os.path.join(output_dir, f"{year} {month:02d}.html")
            
            # Skip if file already exists and is valid
            if os.path.exists(filename) and os.path.getsize(filename) >= 300000:
                continue

            print(f"Downloading {year}/{month:02d}...")
            params = {
                'b': f"{year}{month:02d}",
                'heya': -1, 'shusshin': -1, 'h': 'on', 'sh': 'on', 
                'bd': 'on', 'hd': 'on', 'su': 'on', 'w': 'on', 
                'hr': 'on', 'ho': 'on', 'ch': 'on', 'cs': 'on', 'cr': 'on'
            }

            try:
                response = requests.get(base_url, params=params, timeout=30)
                response.raise_for_status()
                
                # Validation: Check size
                if len(response.content) < 300000:
                    print(f"  Warning: {year} {month:02d} too small, discarding.")
                    next_round.append((year, month))
                else:
                    with open(filename, 'wb') as f:
                        f.write(response.content)
            
            except Exception as e:
                print(f"  Error: {e}. Waiting 10 minutes before retry.")
                time.sleep(600)  # 10 minute wait
                next_round.append((year, month))
            
            time.sleep(1) # 1 second pause between downloads
        
        pending = next_round
        if pending:
            print(f"--- Finished pass. Retrying {len(pending)} failed files. ---")

if __name__ == "__main__":
    download_banzuke()
