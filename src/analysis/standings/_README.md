# Sumo Standings Application

A full-stack, data-driven application that generates and displays historical Sumo wrestling performance metrics. The system uses a **Static-Site Generation (SSG)** model, where a Python engine "pre-bakes" analytical datasets into CSV files for a lightweight JavaScript frontend to consume.

## 1. Architectural Overview
The application is split into three distinct layers to ensure the core analysis is decoupled from the web presentation:

* **The Engine (Python):** Processes canonical Sumo history to calculate wins, bout counts, and statistical consistency (Standard Error, 95% Confidence Intervals).
* **The Publisher (Python):** Orchestrates the engine to generate a suite of standardized datasets (e.g., 6-basho window, 12-basho window) and deploys them to the local server.
* **The Presentation Layer (HTML/JS/CSS):** A responsive web dashboard that allows users to filter, sort, and browse the pre-computed standings.

## 2. The Analytical Model (The Three Axes)
Unlike simple win-loss records, this tool evaluates wrestlers along three specific semantic axes:

1.  **Win Policy:**
    * `FOUGHT_ONLY`: Only wins achieved in a scheduled match.
    * `CREDITED`: Includes *fusensho* (wins by forfeit/default).
2.  **Basho Basis:**
    * `SELECTED`: All tournaments within a time window.
    * `CONTAINING`: Only tournaments where the rikishi actually appeared (adjusts for injury/absence).
3.  **Bout Basis:**
    * `EXPECTED`: Measured against the standard 15 (or 7) bouts.
    * `AVAILABLE`: Measured only against bouts the rikishi actually participated in.

## 3. Component Breakdown

### Backend: Data Production
* **`multiple_basho.py`**: The core logic. It computes ranked totals for any arbitrary window of time.
* **`multiple_basho_view.py`**: The transformation layer. It calculates derived stats (averages/STDEV) and determines **Identity Semantics**: a wrestler's name (*shikona*) and rank (*chii*) are pulled from their latest appearance within the selected window.
* **`publisher.py`**: The build script. It generates the `site_config.json` and all required CSV/JSON pairs, then pushes them to the local server directory (`A:/local/html/standings`).

### Frontend: Web Presentation
* **`index.html`**: A sidebar-driven dashboard.
* **`standings.js`**: A "Sidecar" loader. For every dataset, it loads a CSV (data) and a JSON (metadata). It handles client-side sorting and division filtering (Makuuchi, Juryo, etc.) without server-side processing.
* **`standings.css`**: A dark-mode, high-density data aesthetic for sports analytics.

## 4. Data Flow
1.  **Ingestion:** The Engine loads the canonical `History` object.
2.  **Calculation:** The Engine applies a Win Policy and generates raw totals.
3.  **Refining:** The View layer adds statistical confidence metrics and resolves the wrestler's current rank.
4.  **Publication:** The Publisher saves the result as a CSV and a JSON metadata "sidecar."
5.  **Consumption:** The Browser reads `site_config.json`, fetches the default CSV, and renders the interactive table.

## 5. Deployment
* **Local Server:** The publisher is configured to deploy directly to the `A:/` drive mapping.
* **Remote Host:** TBD. The architecture is designed for "dumb" hosting (any server that can serve static files), making it compatible with legacy Apache or modern CDN environments.

## 6. Project Conventions
* **Identity:** Names and ranks are anchored to the most recent relevant basho in the set.
* **Precision:** Statistical metrics use a symmetric normal-style approximation (Z=1.96) for 95% Confidence Intervals.
* **Persistence:** All runs are timestamped in the `/runs` directory for auditability before being copied to the "live" `/data` folder.
