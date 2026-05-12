# _run.ps1

python -m src.analysis.equelo.expt2 --variant combined

python -m src.analysis.equelo.fixed_v2

python -m src.analysis.banzuke_compare.publisher --date 2026/05 --output-root files/output/bcr

python -m src.products.make_site

