# Shortcuts for paper/build.py. All heavy experiments remain manual.
# Example: make -C paper pdf-with-benchmarks

.PHONY: figures benchmarks tables pdf pdf-with-benchmarks package submission clean

figures:
	python build.py --figures

benchmarks:
	python build.py --benchmarks --benchmark-preset quick --repeats 5

tables:
	python build.py --tables

pdf:
	python build.py

pdf-with-benchmarks:
	python build.py --all --benchmark-preset quick --repeats 5

package:
	python build.py --package

submission:
	python build.py --pdf --package

clean:
	python build.py --clean
