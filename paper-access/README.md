# IEEE Access adaptation v0.1

Separate working manuscript, not submitted and not submission-ready.
DSN v0.22 remains fixed under tag dsn-tool-v0.22-frozen. Do not modify paper/
to perform Access adaptation. Do not submit overlapping versions concurrently.

Official Access template (downloaded 2026-10-02):
https://ieeeaccess.ieee.org/wp-content/uploads/2026/05/ACCESS_latex_template_20260513-1-1.zip
Class, IEEEtran class, bibliography style, font resources, logos and bullet
asset are copied unmodified from the hash-recorded official archive.
No sample authors, photographs, sample DOI or publication dates are claimed.
The sole-author name, college and email were supplied by the author. Romanized
name order and the college's official English wording await author confirmation;
no street or postal address has been supplied.

Initial adaptation uses the official class, an expanded 150--250-word abstract,
keywords and three explicit research questions. Existing results, references,
historical protocols and limitations are preserved; no new measurements.
The contribution is submission/availability tradeoff plus inspectable evidence,
not generalized reliability, parser superiority or GPU savings.

Results now answer RQ1--RQ3 explicitly. Next substantive work: further reduce
historical protocol narrative, assess nearest-method comparison and reproducible
software distribution. Six fixed operations alone do not establish full
research-paper novelty or population effects. Determine necessary additional
evidence before launching experiments. Applied Research is a candidate type,
not yet finalized.

Compile with pdfLaTeX and BibTeX, for example
`latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`.
Tectonic/XeTeX fails at the official template's pdfTeX spot-color primitive.
The 2026-10-02 local build used a portable TeX Live 2026 installation with
`ieeetran` and `courier`; it produced a seven-page PDF. The class was not
modified. The manuscript uses explicit pending publication metadata in place
of the template's default volume/year. PDF compilation does not resolve the
author fields or make the manuscript submission-ready.
The author-update build uses task-local TeX Live at
`/Users/chevalgrand/.cache/paper-access-texlive/bin/universal-darwin`.
Author/source declarations and final human content approval are still required.

Official rapid-review page reports average four weeks submission to accept/reject,
typically four to six weeks to publication; no deadline or acceptance guarantee.
APC page currently states USD2160 plus applicable local taxes. Post-acceptance
guide asks for final files, copyright and APC after acceptance. No pre-acceptance
submission/review charge was identified. Verify live prices before commitment.

Sources:
https://ieeeaccess.ieee.org/about/rapid-peer-review/
https://ieeeaccess.ieee.org/for-authors/article-processing-charges/
https://ieeeaccess.ieee.org/authors/post-acceptance-guide/
https://ieeeaccess.ieee.org/authors/submission-guidelines/
