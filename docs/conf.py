"""Sphinx configuration for the published setup guide."""

project = "Publication Hub"
author = "Chris Mauzey"
language = "en"
root_doc = "index"
extensions = ["sphinx.ext.githubpages"]
exclude_patterns = ["_build", "html", "doctrees", ".venv", "Thumbs.db", ".DS_Store"]
html_theme = "sphinx_rtd_theme"
html_show_copyright = False
html_theme_options = {"navigation_depth": 2}
html_static_path = ["_static"]
html_js_files = ["external-links.js"]

# Example local URLs are verified by the setup smoke tests, not public linkcheck.
linkcheck_ignore = [r"http://127\.0\.0\.1(?::\d+)?/"]
linkcheck_timeout = 15
linkcheck_retries = 1
linkcheck_rate_limit_timeout = 15
