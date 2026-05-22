# _run.ps1

# Equelo fixed-point source data. fixed_v2 and downstream rating consumers
# depend on this output.
python -m src.analysis.equelo.expt2.run_all --start 1958 --end 2026 --modern-end-year 2026 --k-policy divisional --collapse annotation-only

# Rikishi bio enrichment. The downloader refreshes missing raw SumoDB bio HTML;
# the parser regenerates the typed JSON artifact consumed by src.infra.get_bios.api.
python -m src.infra.get_bios
python -m src.infra.get_bios.parser

# Current Equelo process-rating outputs.
python -m src.analysis.equelo.fixed_v2

# Win-probability-by-standing inputs and site bundle. trace_main depends on
# both the empirical matchup output and fixed_v2 day-end ratings.
python -m src.analysis.probability.matchups --start 1958 --end 2026
python -m src.analysis.probability.matchups.trace_main

# Producer bundles consumed directly by make_site.
python -m src.analysis.standings.publisher
python -m src.analysis.banzuke_compare.publisher --output-root files/output/bcr
python -m src.analysis.sumo_history.basho_results --output-root files/output/basho_results

# Legacy/standalone chart artifacts that make_site still copies into the site.
python -m src.misc.finish_by_chii --start 1958 --end 2026 --html-output files/output/misc/finish_by_chii_1958_2026.html --average-html-output files/output/misc/average_finish_by_chii_1958_2026.html --no-upload
python -m src.misc.banzuke_by_era --start 1958 --end 2026
python -m src.misc.makuuchi_by_era --start 1958 --end 2026
python -m src.analysis.persistence --start 1958 --end 2026 --num-basho 10

# Build and deploy the public site from the generated artifacts above.
python -m src.products.make_site --prod
