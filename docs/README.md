# Building the documentation

Follow these steps from the repository root. Run each block separately and wait
for it to finish before continuing, except for the preview server, which stays
running until you stop it.

## Step 1: Create the documentation environment

Install Python 3.12, Bash, and Make. Then create and activate a virtual environment:

```bash
python3.12 -m venv docs/.venv
source docs/.venv/bin/activate
```

Install the documentation dependencies:

```bash
python -m pip install -r docs/requirements.txt
```

## Step 2: Build the HTML documentation

With the documentation environment active:

```bash
make -C docs clean
make -C docs html
```

Sphinx treats warnings as errors. The documentation dependencies are separate
from the application requirements; no Django installation or database is needed.
Build caches stay in the ignored `docs/_build/` directory.

## Step 3: Preview and verify the site

Start the preview server from the repository root:

```bash
python -m http.server 8080 --directory docs/_build/html
```

Leave that terminal open. Open <http://127.0.0.1:8080/> and verify the sidebar links to all five guide pages,
code blocks retain indentation, and the Getting Started entry point works.
In a second terminal, run:

```bash
curl -I http://127.0.0.1:8080/
```

Expect HTTP 200. Press Ctrl-C in the server terminal to stop the preview before
starting another server on port 8080.

## GitHub Pages deployment

The [documentation workflow](../.github/workflows/documentation.yml) builds and
deploys the site on every push to `main`, including merged pull requests. It does
not run on pushes to other branches, pull request events, or manual dispatch.
The build installs the documentation dependencies with Python 3.12 and treats
Sphinx warnings as errors; deployment runs only after a successful build.

### Step 1: Configure GitHub Pages

1. Open the repository's **Settings → Pages → Build and deployment**.
2. Set **Source** to **GitHub Actions**.
3. If the `github-pages` environment has deployment branch restrictions, allow
   `main`.

### Step 2: Build the Pages artifact locally

To build and preview the exact Pages artifact locally, from the repository root
with the documentation virtual environment active:

```bash
make -C docs clean
make -C docs pages
```

### Step 3: Preview the Pages artifact

Stop any previous preview server with Ctrl-C, then run:

```bash
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

### Step 4: Publish and verify

1. Commit the documentation sources and any build or workflow changes.
2. Push or merge those changes to `main`.
3. Open the repository's **Actions** tab and select **Deploy documentation**.
4. Wait for both the build and deploy jobs to succeed.
5. Open the deployment URL from the deploy job. Verify the homepage, sidebar
   navigation, and external links at that URL.

## External-link checks

Optional external-link check (requires internet access):

```bash
python -m sphinx -b linkcheck -W --keep-going -d docs/_build/doctrees docs docs/_build/linkcheck
```

External sites can reject automated checks; investigate failures rather than
assuming every failure means the link is invalid.
