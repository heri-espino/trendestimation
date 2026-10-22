# Manual heavy builds only; keep PDF generation off automated push CI.
.PHONY: figures pdf clean benchmarks
figures:
	python figures/make_figures.py
	python figures/make_extended_figures.py
	python figures/benchmark_orders.py
benchmarks:
	python benchmarks/run_all.py --preset quick --repeats 5
pdf: figures
	latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
clean:
	latexmk -C main.tex
