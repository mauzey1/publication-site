Native development
======================

Prerequisites and checkout
------------------------------

Install Git and Python 3.12 (including ``venv`` and pip). These commands use Bash
on macOS, Linux, or Windows through WSL. PostgreSQL and Docker are not required.
From the directory where you keep checkouts:

.. code-block:: bash

   git clone https://github.com/aims-group/publication-site.git
   cd publication-site/pubhub
   python3.12 -m venv .venv
   source .venv/bin/activate
   python --version
   python -m pip install -r requirements.txt

The version check should report Python 3.12.x. All remaining management commands
run from ``publication-site/pubhub`` with this virtual environment active.

Create the database and administrator
-----------------------------------------

``manage.py`` defaults to ``config.settings.local`` unless
``DJANGO_SETTINGS_MODULE`` is already set. Clear a value left from Docker or
production, apply the committed migrations, and create a login:

.. code-block:: bash

   unset DJANGO_SETTINGS_MODULE
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py check
   python manage.py migrate --check

Enter an administrator username, email, and password at the prompts. The checks
should exit successfully with no pending migrations. SQLite stores the database
in ``pubhub/local.sqlite3``, which Git ignores. This is a new database with no
publications. If desired, load the bundled climate project tags and journals:

.. code-block:: bash

   python manage.py initialize

See :ref:`metadata` for its contents and verification. You can skip initialization
and define your own projects and metadata through the administrator interface.

Run and verify
------------------

From ``publication-site/pubhub``, with migrations applied:

.. code-block:: bash

   python manage.py runserver

Open http://127.0.0.1:8000/ and log in at http://127.0.0.1:8000/admin/ using the
administrator you created. In another terminal (any directory):

.. code-block:: bash

   curl -I http://127.0.0.1:8000/
   curl -I http://127.0.0.1:8000/static/uswds/css/uswds.min.css

Both should return HTTP 200. Local settings enable debug mode, console logging,
and a development secret key. WhiteNoise finds development assets in
``pubhub/pubhub-static``; collecting static files is not needed for this path.
The local settings are for development only.

Stop and resume
-------------------

Press Ctrl-C in the server terminal to stop it. The SQLite file retains your
accounts and publications. In a new terminal, from your checkout root:

.. code-block:: bash

   cd pubhub
   source .venv/bin/activate
   unset DJANGO_SETTINGS_MODULE
   python manage.py migrate
   python manage.py runserver

The homepage and administrator login should work again with the existing data.
Rerun the HTTP checks above. After pulling dependency changes, rerun
``python -m pip install -r requirements.txt`` before migrating. ``deactivate``
leaves the virtual environment when you finish.
