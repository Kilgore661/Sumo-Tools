# _run.ps1
python -m src.analysis.equelo.expt2.run_all --start 1958 --end 2026 --modern-end-year 2026 --k-policy divisional --collapse annotation-only

python -m src.analysis.equelo.fixed_v2

python -m src.analysis.probability.matchups --start 1958 --end 2026

python -m src.analysis.probability.matchups.trace_main

python -m src.analysis.standings.publisher

python -m src.analysis.banzuke_compare.publisher --output-root files/output/bcr

python -m src.analysis.sumo_history.basho_results --output-root files/output/basho_results

python -m src.misc.finish_by_chii --start 1958 --end 2026 --html-output files/output/misc/finish_by_chii_1958_2026.html --average-html-output files/output/misc/average_finish_by_chii_1958_2026.html --no-upload

python -m src.misc.banzuke_by_era --start 1958 --end 2026

python -m src.misc.makuuchi_by_era --start 1958 --end 2026

python -m src.analysis.persistence --start 1958 --end 2026 --num-basho 10

python -m src.products.make_site --prod
