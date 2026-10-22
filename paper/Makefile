# Manual LaTeX build. No CI/push-triggered heavy runs.
.PHONY: pdf figures clean
figures:
	python figures/make_figures.py
pdf: figures
	latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex
clean:
	latexmk -C -outdir=build main.tex
