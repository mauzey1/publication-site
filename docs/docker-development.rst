Docker development
==================

Run Publication Hub locally with Docker Compose and PostgreSQL. Follow the steps
below in order. The application runs in a Python 3.12 container and uses
PostgreSQL 16.3.

Step 1: Check the prerequisites
-------------------------------

Install Git, Docker Engine (or Docker Desktop), and Docker Compose v2. Start
Docker, then run these checks from any directory:

.. code-block:: bash

   docker info
   docker compose version

Both commands should succeed, and Compose should report version 2 or later.
Ports 8000 and 5433 and container names ``django`` and ``postgres`` must be free.
The checked-in Compose file publishes these ports on all host interfaces, so
use this setup on a trusted development machine.

Step 2: Download the code
-------------------------

From the directory where you want to store the repository:

.. code-block:: bash

   git clone https://github.com/aims-group/publication-site.git
   cd publication-site/pubhub
   mkdir -p .envs

Run all remaining commands from ``publication-site/pubhub``.

Step 3: Create the environment files
------------------------------------

Create ``.envs/.django`` with the following contents. These example credentials
are for local development only. If the file already exists, review its values
before making changes.

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

Git ignores both files. Compose loads their values into the containers when it
creates them. ``DJANGO_SETTINGS_MODULE=config.settings.docker`` selects the
PostgreSQL settings. Containers connect to PostgreSQL at ``postgres:5432``;
tools on your host connect at ``localhost:5433``.

For email, ``localhost`` refers to the Django container. No mail server is
included; see :ref:`email` before testing password reset.

Step 4: Build and start the containers
--------------------------------------

With the environment files in place, from ``publication-site/pubhub``:

.. code-block:: bash

   docker compose config --quiet

If validation succeeds, build the images and start the containers:

.. code-block:: bash

   docker compose up --build -d

Follow the startup logs in a separate command:

.. code-block:: bash

   docker compose logs -f django

Wait until the logs show that the development server is listening on port 8000.
Startup waits for PostgreSQL, generates and applies database migrations,
collects static files, and loads the bundled metadata with ``initialize``.
These steps run automatically. The database initially has no publications.

Press Ctrl-C to exit the log viewer. The containers keep running.

Step 5: Create an administrator account
---------------------------------------

Run the following command and enter a username, email address, and password at
the prompts. Run it by itself and wait for it to finish before continuing:

.. code-block:: bash

   docker compose exec django python manage.py createsuperuser

Step 6: Verify the site
-----------------------

Check the application, database migrations, and HTTP responses:

.. code-block:: bash

   docker compose exec django python manage.py check
   docker compose exec django python manage.py migrate --check
   docker compose ps
   curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/
   curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/static/uswds/css/uswds.min.css

Both services should be running, the management checks should succeed, and both URLs
should return HTTP 200. Log in at http://127.0.0.1:8000/admin/ with your new
administrator account. Registration separately requires :ref:`recaptcha`.

Use GET requests as shown above. The homepage returns HTTP 405 for HEAD requests
(``curl -I``), even when the site is working.

Apply changes
-------------

The application code is copied into the image when it is built. After changing
Python code, templates, static assets, or dependencies, rebuild the image and
recreate the containers:

.. code-block:: bash

   docker compose up --build -d
   docker compose logs --tail=100 django postgres

Repeat the checks in step 6 after the build. Restarting a container uses its
existing image. After changing environment files, recreate the containers:

.. code-block:: bash

   docker compose up -d --force-recreate

Stop and resume
---------------

To stop the containers:

.. code-block:: bash

   docker compose stop

To start them again:

.. code-block:: bash

   docker compose start
   docker compose ps

Alternatively, ``docker compose down`` removes containers and the network;
``docker compose up -d`` recreates them. Named volumes retain the database
(``local_postgres_data``), database backups (``local_postgres_data_backups``), and
Django logs (``local_django_log``). Compose prefixes their names with its project
name, normally ``pubhub``; keep that name and checkout directory stable to reuse
the same data. Verify persistence by signing in with the same administrator after
restarting. Do not use ``down -v`` for routine maintenance: it deletes those volumes.
