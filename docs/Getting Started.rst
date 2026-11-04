Getting Started
===================

Choose your setup
---------------------

Choose the guide that matches where you want to run Publication Hub. Each guide
walks through installation, configuration, startup, and verification in order.

* :doc:`native-development`: run locally with Python 3.12 and SQLite.
  Choose this for the simplest development setup, without Docker.
* :doc:`docker-development`: run locally with Docker Compose and PostgreSQL.
  Choose this to develop with a PostgreSQL database. Startup also loads the
  bundled climate metadata.
* :doc:`production`: host the site on a Linux server with PostgreSQL, Gunicorn,
  and Traefik. This guide requires a domain and an existing TLS certificate.

Run the commands in Bash. Both development guides support macOS, Linux, or
Windows through WSL; the production guide assumes a Linux server. Each step
states which directory to use. Replace example domains, file paths, and secret
values where instructed.

Run command blocks in order and wait for each command to succeed before
continuing. Commands that ask for input, such as ``createsuperuser``, have their
own blocks. Answer their prompts before pasting another command. Server and log
viewer commands also have separate blocks; follow the instructions beside each
block to leave it running or stop it. Blocks labeled as file contents belong in
the named file, rather than in the terminal.

Test one setup at a time unless you have configured separate ports, container
names, and Compose project names. Native and Docker development both use port
8000, and both Docker guides normally use the Compose project name ``pubhub``.

A new database has no publications. The optional ``initialize`` command adds
project tags and journal names. Add publication records through the application
after setup. See :doc:`configuration` to configure registration and email, learn
about the bundled metadata, or troubleshoot a problem.

Existing installations
--------------------------

The production guide is for a fresh database. For an established installation,
read the `migration helper documentation
<https://github.com/aims-group/publication-site/blob/main/pubhub/scripts/migration/README.md>`_
before changing Django or PostgreSQL versions or restoring data.
