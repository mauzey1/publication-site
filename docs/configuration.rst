Configuration and troubleshooting
=====================================

Settings and environment
----------------------------

Management commands run from ``publication-site/pubhub``. Native commands need
the virtual environment activated. ``manage.py`` defaults to
``config.settings.local``; Docker development must explicitly select
``config.settings.docker`` and production must select
``config.settings.production`` through ``DJANGO_SETTINGS_MODULE``.

Native Python does not automatically load ``.env`` or ``.envs`` files. Export
supported variables in your shell before starting the server. Compose loads the
``env_file`` paths in its YAML into containers; the proxy's ``.env`` supplies
Compose build arguments instead. Recreate application containers after changing
environment files. Rebuild Traefik after changing its domain or prefix.

The settings modules in ``pubhub/config/settings/`` are the source of truth.
Only variables read there are supported. In particular, do not assume that
arbitrary Django setting names become environment options. Several booleans use
raw ``os.environ.get`` values, so a string such as ``False`` or ``0`` is nonempty
and can enable an option. Keep the production security defaults. Local and Docker
development settings always enable debug mode; production always disables it.

.. _metadata:

Optional climate metadata
-----------------------------

After migrations, from ``publication-site/pubhub`` in the native virtual
environment:

.. code-block:: bash

   python manage.py initialize
   python manage.py shell -c "from publisher.models import Project, JournalOptions, Publication; print('Projects:', Project.objects.count(), 'Journals:', JournalOptions.objects.count(), 'Publications:', Publication.objects.count())"

Expect nonzero project and journal counts, and zero publications on a fresh
installation. The initializer reads ``scripts/activity.py``, ``experiment.py``,
``frequency.py``, ``keyword.py``, ``model.py``, ``realm.py``, ``variable.py``, and
``journals.py``. It creates projects, controlled vocabulary, project/tag
relationships, and journal names. It does not import publications or users.
Repeated runs skip existing entries; they do not remove old metadata.

Docker development runs this automatically at startup. For the verification
command above in Docker, prefix ``python`` with ``docker compose exec django``.
For production, use ``docker compose -p pubhub -f docker-compose.prod.yml -f
compose.deployment.yml exec django``. Production initialization is the optional
one-off command in :doc:`production`. To use different metadata, manage it through
the admin interface or customize the scripts; script changes require rebuilding
Docker images.

.. _recaptcha:

Registration and reCAPTCHA
------------------------------

Public registration at ``/accounts/register/`` uses a reCAPTCHA v2 checkbox.
Register the site's domain with `Google reCAPTCHA
<https://www.google.com/recaptcha/admin/create>`_ and set
``RECAPTCHA_PUBLIC_KEY`` (site key) and ``RECAPTCHA_PRIVATE_KEY`` (secret key).
Use keys registered for your development hostname when testing locally. Blank
values in the setup examples do not provide working registration. Browser access
to Google and server-side verification access are required.

For native development, export both values before starting ``runserver``. For
Docker, put them in the appropriate Django environment file and recreate the
container using the commands in its setup guide. Verify by completing a
registration in the browser. ``createsuperuser`` and ordinary login do not use
reCAPTCHA, so they work before these keys are configured.

.. _email:

Email and password reset
----------------------------

The shipped settings support ``EMAIL_HOST``, ``EMAIL_PORT``, and
``DEFAULT_FROM_EMAIL`` as environment variables. Django's default SMTP backend
is used. The defaults are ``localhost:1025``; no SMTP server is bundled. In a
container, ``localhost`` refers to that container. Use a reachable SMTP relay or
mail catcher for testing, then configure an appropriate relay for deployment.

The shipped settings do not read ``EMAIL_HOST_USER``, ``EMAIL_HOST_PASSWORD``,
``EMAIL_USE_TLS``, ``EMAIL_USE_SSL``, or ``EMAIL_BACKEND`` from the environment.
Adding these names to an environment file alone has no effect. An SMTP provider
requiring authentication or TLS needs a separately maintained Django settings
module that configures those settings, or a suitable relay. Do not enter provider
credentials in unsupported environment fields and expect delivery to work.

With a relay configured, from ``publication-site/pubhub`` and the active native
virtual environment, replace the recipient with a mailbox you control:

.. code-block:: bash

   python manage.py shell -c "from django.core.mail import send_mail; from django.conf import settings; print(send_mail('Publication Hub mail test', 'SMTP is configured.', settings.DEFAULT_FROM_EMAIL, ['operator@example.org'], fail_silently=False))"

For Docker, use the command prefixes described under :ref:`metadata`. Expect
``1`` and confirm receipt. Then exercise ``/accounts/password_reset/`` with the
email address of an existing active user. A success page alone does not prove
email delivery.

Troubleshooting
-------------------

Use the working directory and command prefix for your selected setup. Native
errors appear in the server terminal; Docker startup output appears in
``docker compose logs`` (with the production project's two ``-f`` flags when
applicable). Request logs in Docker are at
``/var/log/django/publications-site.log`` with the documented environment.

Missing environment files or wrong database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run ``docker compose config --quiet`` with the same files and project name used
to launch the stack. A missing ``env_file`` stops Compose before startup. A native
command unexpectedly requesting PostgreSQL usually has a leftover
``DJANGO_SETTINGS_MODULE``; unset it. Conversely, Docker using SQLite means the
Docker settings module was not selected. A production error involving
``NoneType`` and ``split`` commonly means ``DJANGO_ALLOWED_HOSTS`` is missing.

Waiting for PostgreSQL or authentication failure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Inspect the PostgreSQL logs and confirm ``POSTGRES_HOST=postgres`` and
``POSTGRES_PORT=5432`` inside containers. The host's development port 5433 must
not be used between services. Production Django needs both networks from the
override. Check database connectivity from ``publication-site/pubhub``:

.. code-block:: bash

   docker compose exec django python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print(connection.vendor)"

Expect ``postgresql``; use the full production prefix for production. If Django
cannot stay running, use ``run --rm django`` instead of ``exec django`` (the
entrypoint still waits for the database). PostgreSQL initializes credentials only
when its data directory is empty. Changing environment passwords does not update
an existing role. Restore the matching configuration or deliberately change the
role credentials; do not delete a database volume to fix an authentication error.

Missing tables or metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run ``python manage.py migrate --check`` and then ``python manage.py migrate``
if migrations are pending, using your environment's prefix. Production startup
does not migrate. An empty publication list is expected on a new database.
``initialize`` adds metadata only; see :ref:`metadata`.

Permission denied for the log file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set ``DJANGO_LOGGING_FILENAME=/var/log/django/publications-site.log`` and recreate
the container. Production runs as UID/GID 10001 by default. If reusing an older
log volume, inspect its ownership and arrange write access for the image's user;
keep the application running as its non-root user. Native settings use console
logging and do not need this directory.

HTTP 400, gateway errors, or missing static files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

HTTP 400 can mean a hostname absent from ``DJANGO_ALLOWED_HOSTS``. A Traefik 404
can mean the requested host differs from the domain baked into its image; rebuild
the proxy after correcting ``traefik/.env``. A 502/504 can mean Django is stopped,
unhealthy, or not on ``traefik_default``. Check both services' logs and network
membership. A stale page or static asset after source edits in Docker needs an
image rebuild. Confirm startup completed static collection and repeat the static
asset HTTP check from your setup guide.

Certificate or port errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A default/untrusted certificate usually means the certificate bind mount is
missing, filenames differ from ``cert.pem``/``key.pem``, or Traefik cannot read
them. Confirm the certificate chain, expiry, domain, matching key, and any
symlink targets. Use the proxy logs and ``curl -I https://YOUR_DOMAIN/``;
fix verification failures before accepting the deployment.

An address already in use error means another process/container owns a required
port. Docker development also hardcodes the names ``django`` and ``postgres``,
so changing only the Compose project name cannot run a second development stack.
Stop the conflicting stack or provide deployment-specific port/name overrides.
Production and development both default to the Compose project name ``pubhub``;
use separate checkouts/hosts or deliberate project names if running both.

Database upgrades and recovery
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Do not point a newer PostgreSQL major version at an older data volume. Follow the
`migration helper documentation
<https://github.com/aims-group/publication-site/blob/main/pubhub/scripts/migration/README.md>`_
for backup, restore rehearsal, and established-installation checks. Keep project
names, environment files, and override files consistent with the installation
being operated on.
