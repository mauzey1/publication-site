# Building the documentation

Prerequisites: Python 3.12, Bash, and Make. From the repository root:

```bash
python3.12 -m venv docs/.venv
source docs/.venv/bin/activate
python -m pip install -r docs/requirements.txt
make -C docs clean
make -C docs html
```

Sphinx treats warnings as errors. The documentation dependencies are separate
from the application requirements; no Django installation or database is needed.
Build caches stay in the ignored `docs/_build/` directory.

Preview from the repository root:

```bash
python -m http.server 8080 --directory docs/_build/html
```

Open <http://127.0.0.1:8080/>. Verify the sidebar links to all five guide pages,
code blocks retain indentation, and the Getting Started entry point works.
`curl -I http://127.0.0.1:8080/` should return HTTP 200. Ctrl-C stops the preview.

## GitHub Pages deployment

The [documentation workflow](../.github/workflows/documentation.yml) builds and
deploys the site on every push to `main`, including merged pull requests. It does
not run on pushes to other branches, pull request events, or manual dispatch.
The build installs the documentation dependencies with Python 3.12 and treats
Sphinx warnings as errors; deployment runs only after a successful build.

In the repository's **Settings → Pages → Build and deployment**, set **Source**
to **GitHub Actions**. If the `github-pages` environment has deployment branch
restrictions, allow `main`. Commit and push the workflow and documentation sources
to `main`; the deployment URL appears in the workflow's deploy job. Verify that
the homepage, sidebar navigation, and external links work at that URL.

To build and preview the exact Pages artifact locally, from the repository root
with the documentation virtual environment active:

```bash
make -C docs clean
make -C docs pages
python -m http.server 8080 --directory docs/_build/pages
```

Open <http://127.0.0.1:8080/>; it should redirect to `/html/index.html`. The
`/html/Getting%20Started.html` entry point also remains available. Ctrl-C stops
the preview.

The artifact contains the freshly built site under `html/`, the root redirect
from `docs/index.html`, and `docs/.nojekyll`. Build caches and `.buildinfo` files
are excluded. Commit the Sphinx sources, build configuration, and custom assets;
generated HTML stays in the ignored `docs/_build/` directory and is uploaded by
the workflow. The former `docs/html/` output directory is also ignored.
`docs/index.html` is the hand-maintained redirect copied into the artifact.

## External-link checks

Optional external-link check (requires internet access):

```bash
python -m sphinx -b linkcheck -W --keep-going -d docs/_build/doctrees docs docs/_build/linkcheck
```

External sites can reject automated checks; investigate failures rather than
assuming every failure means the link is invalid.
