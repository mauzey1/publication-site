Native development
==================

Run Publication Hub locally with Python and SQLite. Follow the steps below in
order. This setup is intended for development.

Step 1: Check the prerequisites
-------------------------------

Install Git and Python 3.12 (including ``venv`` and pip). These commands use Bash
on macOS, Linux, or Windows through WSL. PostgreSQL and Docker are not required.
Check that Python 3.12 is available:

.. code-block:: bash

   python3.12 --version

The command should report Python 3.12.x.

Step 2: Download the code and install dependencies
--------------------------------------------------

From the directory where you want to store the repository:

.. code-block:: bash

   git clone https://github.com/aims-group/publication-site.git
   cd publication-site/pubhub

Create and activate a virtual environment:

.. code-block:: bash

   python3.12 -m venv .venv
   source .venv/bin/activate

Install the application dependencies:

.. code-block:: bash

   python -m pip install -r requirements.txt

Run all remaining management commands from ``publication-site/pubhub`` with
this virtual environment active.

Step 3: Create the database and administrator account
-----------------------------------------------------

``manage.py`` defaults to ``config.settings.local`` unless
``DJANGO_SETTINGS_MODULE`` is already set. Clear any existing value so the
commands use the local SQLite settings, then create the database tables and
administrator account:

.. code-block:: bash

   unset DJANGO_SETTINGS_MODULE
   python manage.py migrate

Create the administrator account. Run this command by itself, then enter a
username, email address, and password when prompted. Wait for it to finish
before entering the next command.

.. code-block:: bash

   python manage.py createsuperuser

Check the application and confirm that all migrations have been applied:

.. code-block:: bash

   python manage.py check
   python manage.py migrate --check

Both checks should finish without errors, with no pending migrations. The database is saved as
``local.sqlite3`` in the current directory. Git ignores this file.

Step 4: Load optional climate metadata
--------------------------------------

The new database contains no publications. To add the bundled climate project
tags and journal names, run:

.. code-block:: bash

   python manage.py initialize

See :ref:`metadata` for its contents and verification. You can skip initialization
and define your own projects and metadata through the administrator interface.

Step 5: Start the development server
------------------------------------

From ``publication-site/pubhub``, with migrations applied:

.. code-block:: bash

   python manage.py runserver

Leave this terminal open while the server runs.

Step 6: Verify the site
-----------------------

Open http://127.0.0.1:8000/ and sign in at http://127.0.0.1:8000/admin/ with the
administrator account you created. In a second terminal, from any directory,
check the homepage and a static asset:

.. code-block:: bash

   curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/
   curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/static/uswds/css/uswds.min.css

Both requests should return HTTP 200. These commands use GET because the
homepage does not accept HEAD requests (``curl -I``).

Local settings enable debug mode, console logging,
and a development secret key. WhiteNoise finds development assets in
``pubhub/pubhub-static``; collecting static files is not needed for this path.
For public registration and password reset, complete the additional setup in
:doc:`configuration`.

Stop and resume
---------------

Press Ctrl-C in the server terminal to stop it. The SQLite file retains your
accounts and publications. In a new terminal, from your checkout root:

.. code-block:: bash

   cd pubhub
   source .venv/bin/activate
   unset DJANGO_SETTINGS_MODULE
   python manage.py migrate

Start the server and leave this terminal open:

.. code-block:: bash

   python manage.py runserver

The homepage and administrator login should work again with the existing data.
Repeat the HTTP checks in step 6. If an update changes the dependencies, run
``python -m pip install -r requirements.txt`` before applying migrations.
Run ``deactivate`` to leave the virtual environment when you finish.
