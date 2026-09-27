.PHONY: pdf audit figures package clean
PYTHON ?= python3
pdf: audit
	latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
audit:
	$(PYTHON) scripts/audit_retained_evidence.py
figures:
	$(PYTHON) scripts/build_figures.py
package:
	$(PYTHON) scripts/package_manuscript.py
clean:
	latexmk -c main.tex
