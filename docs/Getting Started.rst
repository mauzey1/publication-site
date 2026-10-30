Getting Started
===================

Choose your setup
---------------------

* :doc:`native-development`: Python 3.12, a virtual environment, and SQLite.
  Start here for the simplest local development setup.
* :doc:`docker-development`: Docker Compose, PostgreSQL, and an application
  image. Startup also loads the bundled climate metadata.
* :doc:`production`: a new Linux deployment with PostgreSQL, Gunicorn, Traefik,
  and an existing TLS certificate.

All commands target Bash on macOS, Linux, or Windows through WSL; production
commands target a Linux host. Each guide states the working directory. Commands
that keep running should be left in their terminal while you verify the site
from another terminal or a browser.

A new database has no publications. The optional metadata initializer supplies
project tags and journal names; it does not import publication records. See
:doc:`configuration` for metadata, registration, email, and troubleshooting.

Existing installations
--------------------------

The production guide is for a fresh database. For an established installation,
read the `migration helper documentation
<https://github.com/aims-group/publication-site/blob/main/pubhub/scripts/migration/README.md>`_
before changing Django or PostgreSQL versions or restoring data.
