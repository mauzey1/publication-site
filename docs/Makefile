SPHINXBUILD ?= python -m sphinx
SPHINXOPTS ?= -W --keep-going

.PHONY: html pages clean

html:
	$(SPHINXBUILD) -b html $(SPHINXOPTS) -d _build/doctrees . _build/html

# Preserve the existing root redirect and /html/ URLs in the Pages artifact.
pages: html
	python -c "from pathlib import Path; import shutil; p = Path('_build/pages'); shutil.rmtree(p) if p.exists() else None; shutil.copytree('_build/html', p / 'html', ignore=shutil.ignore_patterns('.buildinfo*')); shutil.copy2('index.html', p / 'index.html'); shutil.copy2('.nojekyll', p / '.nojekyll')"

clean:
	python -c "import shutil; shutil.rmtree('_build', ignore_errors=True)"
