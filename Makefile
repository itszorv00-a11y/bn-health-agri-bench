PY := python3

.PHONY: validate test iaa eval stats figures paper

validate:
	$(PY) scripts/validate_data.py data/seed/seed_questions.json

test:
	$(PY) -m pytest tests/ -q

iaa:
	$(PY) scripts/compute_iaa.py data/gold/annotations.csv

eval:
	$(PY) scripts/run_eval.py --questions data/gold/questions.json \
		--out data/results/records.jsonl

stats:
	$(PY) scripts/bootstrap_stats.py --records data/results/records.jsonl \
		--annotations data/gold/annotations.csv --out data/results/stats.json

figures:
	$(PY) scripts/make_figures.py --out figures/

paper:
	cd paper && pdflatex -interaction=nonstopmode main.tex && bibtex main && \
	pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex
