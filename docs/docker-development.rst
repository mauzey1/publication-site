Docker development
======================

Prerequisites and environment files
---------------------------------------

Install Git, Docker Engine (or Docker Desktop), and Docker Compose v2. Start
Docker and verify ``docker info`` and ``docker compose version`` from any
directory. The stack uses PostgreSQL 16.3 and a Python 3.12 application image.
Ports 8000 and 5433 and container names ``django`` and ``postgres`` must be free.
The checked-in Compose file publishes these ports on all host interfaces, so
use this setup on a trusted development machine.

From the directory where you keep checkouts:

.. code-block:: bash

   git clone https://github.com/aims-group/publication-site.git
   cd publication-site/pubhub
   mkdir -p .envs

All remaining commands run from ``publication-site/pubhub``. Create
``.envs/.django`` with these complete, development-only contents:

.. code-block:: text

   DJANGO_SETTINGS_MODULE=config.settings.docker
   DJANGO_SECRET_KEY=unsafe-local-development-key
   DJANGO_LOGGING_FILENAME=/var/log/django/publications-site.log
   DJANGO_LOGGING_LEVEL=INFO
   RECAPTCHA_PUBLIC_KEY=
   RECAPTCHA_PRIVATE_KEY=
   EMAIL_HOST=localhost
   EMAIL_PORT=1025
   DEFAULT_FROM_EMAIL=Publication Hub <noreply@localhost>

Create ``.envs/.postgres``:

.. code-block:: text

   POSTGRES_HOST=postgres
   POSTGRES_PORT=5432
   POSTGRES_DB=pubhub
   POSTGRES_USER=pubhub
   POSTGRES_PASSWORD=unsafe-local-database-password

Do not replace existing environment files without reviewing them. These files
are ignored by Git. Compose injects their values into the containers;
``manage.py`` alone does not read them. The explicit settings module selects
PostgreSQL instead of the native SQLite default. Inside Docker, PostgreSQL is
``postgres:5432``; from the host it is ``localhost:5433``. ``EMAIL_HOST=localhost``
here means the Django container, not your host; see :ref:`email` before testing
password reset.

Build, start, and verify
----------------------------

With the environment files in place, from ``publication-site/pubhub``:

.. code-block:: bash

   docker compose config --quiet
   docker compose up --build -d
   docker compose logs -f django

Startup waits for PostgreSQL, runs migration generation and migration application,
collects static files, runs ``initialize``, and starts the development server on
port 8000. This is the existing startup script's behavior; there is no need to
run those steps separately. Metadata initialization does not create publications.
When the server is ready, Ctrl-C exits the log viewer without stopping the stack.

.. code-block:: bash

   docker compose exec django python manage.py createsuperuser
   docker compose exec django python manage.py check
   docker compose exec django python manage.py migrate --check
   docker compose ps
   curl -I http://127.0.0.1:8000/
   curl -I http://127.0.0.1:8000/static/uswds/css/uswds.min.css

Both services should be running, management checks should succeed, and both URLs
should return HTTP 200. Log in at http://127.0.0.1:8000/admin/ with your new
administrator account. Registration separately requires :ref:`recaptcha`.

Changes, logs, and persistence
----------------------------------

The current Compose configuration does **not** mount the source tree. Python,
template, static asset, and dependency changes require a rebuild and recreation:

.. code-block:: bash

   docker compose up --build -d
   docker compose logs --tail=100 django postgres

Recheck the URLs above after the build. A container restart alone uses the old
image. After environment-file changes, use ``docker compose up -d --force-recreate``.
To pause and resume the existing containers:

.. code-block:: bash

   docker compose stop
   docker compose start
   docker compose ps

Alternatively, ``docker compose down`` removes containers and the network;
``docker compose up -d`` recreates them. Named volumes retain the database
(``local_postgres_data``), database backups (``local_postgres_data_backups``), and
Django logs (``local_django_log``). Compose prefixes their names with its project
name, normally ``pubhub``; keep that name and checkout directory stable to reuse
the same data. Verify persistence by signing in with the same administrator after
restarting. Do not use ``down -v`` for routine maintenance: it deletes those volumes.
