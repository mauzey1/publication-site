Production deployment
=========================

Prerequisites
-----------------

This procedure creates a **new installation** on a Linux host with Git, Docker
Engine, Docker Compose v2, Bash, and OpenSSL. From any directory, verify
``docker info``, ``docker compose version``, and ``openssl version``. You need:

* A domain such as ``publications.example.org`` with DNS pointing to the host.
* An existing TLS certificate chain and matching private key for that domain.
  Traefik does not obtain or renew certificates in this configuration.
* Ports 80 and 443 available and reachable by your users. The application Compose
  file also publishes port 5000; restrict external access to it with host/network
  rules that cover Docker-published ports so requests enter through Traefik.
* A location for off-host database backups.

Use the domain root. Leave ``DOMAIN_SUBDIRECTORY`` empty; this guide does not
configure Django for a URL subdirectory. The bundled proxy sends HSTS headers,
including subdomains, so use a domain whose subdomains support HTTPS.
For an existing database, follow the migration links in :doc:`Getting Started`.

Checkout and environment
----------------------------

From the directory where you keep deployments:

.. code-block:: bash

   git clone https://github.com/aims-group/publication-site.git
   cd publication-site
   mkdir -p pubhub/.envs
   openssl rand -hex 32
   openssl rand -hex 32

Save the first random value as the Django secret key and the second as the
PostgreSQL password. From the checkout root, create ``pubhub/.envs/.prod.env``
with the following contents, replacing both ``REPLACE_WITH_...`` placeholders
and the example domain:

.. code-block:: text

   DJANGO_SETTINGS_MODULE=config.settings.production
   DJANGO_SECRET_KEY=REPLACE_WITH_FIRST_RANDOM_VALUE
   DJANGO_ALLOWED_HOSTS=publications.example.org
   DJANGO_LOGGING_FILENAME=/var/log/django/publications-site.log
   DJANGO_LOGGING_LEVEL=INFO
   POSTGRES_HOST=postgres
   POSTGRES_PORT=5432
   POSTGRES_DB=pubhub
   POSTGRES_USER=pubhub
   POSTGRES_PASSWORD=REPLACE_WITH_SECOND_RANDOM_VALUE
   RECAPTCHA_PUBLIC_KEY=
   RECAPTCHA_PRIVATE_KEY=
   EMAIL_HOST=localhost
   EMAIL_PORT=1025
   DEFAULT_FROM_EMAIL=Publication Hub <noreply@publications.example.org>

``DJANGO_ALLOWED_HOSTS`` is a comma-separated list of hostnames without schemes
or paths. The explicit log path is required: the image runs as a non-root user
and provides a writable ``/var/log/django`` directory. The default log path
outside that directory is not writable. Registration and password reset need
additional service configuration; see :doc:`configuration`.

From the checkout root, protect the environment file:

.. code-block:: bash

   chmod 600 pubhub/.envs/.prod.env

Compose reads this ignored file at container creation. Keep it private and backed
up; a database password change in the file does not change an existing database
role's password.

Connect Django to PostgreSQL
--------------------------------

From the checkout root, create ``pubhub/compose.deployment.yml``:

.. code-block:: yaml

   services:
     django:
       networks:
         - default
         - traefik_default
   networks:
     default: {}

The checked-in production Compose file attaches Django only to the external
proxy network while PostgreSQL uses the default application network. This
deployment override gives Django access to both. All application commands below
include both files. Keep this operator-created override with your deployment
configuration; it need not be committed to the repository.

Configure and start Traefik
-------------------------------

On the Linux host, place your certificate chain at
``/etc/publication-hub/tls/cert.pem`` and its private key at
``/etc/publication-hub/tls/key.pem``. For example, from any directory, replacing
the two source paths with your existing certificate files:

.. code-block:: bash

   sudo install -d -m 700 /etc/publication-hub/tls
   sudo install -m 644 /path/to/fullchain.pem /etc/publication-hub/tls/cert.pem
   sudo install -m 600 /path/to/privkey.pem /etc/publication-hub/tls/key.pem
   sudo openssl x509 -in /etc/publication-hub/tls/cert.pem -noout -subject -dates

The output should identify your domain's certificate and a valid date range.
Traefik's root user must be able to read both files. Copy actual certificate
contents: symlinks to files outside the mounted directory will not resolve inside
the container.

From the checkout root, create ``traefik/.env``:

.. code-block:: text

   DOMAIN_NAME=publications.example.org
   DOMAIN_SUBDIRECTORY=

Create ``traefik/compose.deployment.yml``:

.. code-block:: yaml

   services:
     traefik:
       volumes:
         - /etc/publication-hub/tls:/etc/traefik/ssl:ro

Compose replaces the original volume mount at ``/etc/traefik/ssl`` with this
read-only bind mount. Traefik expects the filenames ``cert.pem`` and ``key.pem``.
The domain and subdirectory are baked into the proxy image during its build.
From the checkout root:

.. code-block:: bash

   cd traefik
   docker compose -p traefik -f docker-compose.prod.yml -f compose.deployment.yml config --quiet
   docker compose -p traefik -f docker-compose.prod.yml -f compose.deployment.yml up --build -d
   docker network inspect traefik_default --format '{{.Name}}'

The final command should print ``traefik_default``. Always use ``-p traefik``:
it creates the external network expected by the application. Until Django starts,
the proxy may return a gateway error.

Build and initialize the application
----------------------------------------

From ``publication-site/traefik``, enter the application directory:

.. code-block:: bash

   cd ../pubhub
   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml config --quiet
   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml build
   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml up -d postgres
   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml run --rm django python manage.py migrate
   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml run --rm django python manage.py createsuperuser

The application entrypoint waits for PostgreSQL. Migrations should finish
successfully and administrator creation should prompt for your credentials.
Optionally load bundled climate metadata (no publication records):

.. code-block:: bash

   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml run --rm django python manage.py initialize

Launch and verify
---------------------

Still in ``publication-site/pubhub``:

.. code-block:: bash

   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml up -d
   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml exec django python manage.py check
   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml exec django python manage.py migrate --check
   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml ps
   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml logs --tail=100 django postgres

Production startup collects static files and starts Gunicorn on port 5000.
It does **not** run migrations or initialize metadata; those explicit commands
above are required when appropriate. The checks should succeed and both services
should remain running. From any directory, using your real domain:

.. code-block:: bash

   curl -I http://publications.example.org/
   curl -I https://publications.example.org/
   curl -I https://publications.example.org/static/uswds/css/uswds.min.css

Expect an HTTP-to-HTTPS redirect and HTTP 200 for both HTTPS requests, with a
trusted certificate. Open ``https://publications.example.org/admin/`` and sign in.
To test before DNS changes, use ``curl --resolve publications.example.org:443:HOST_IP
-I https://publications.example.org/``, replacing ``HOST_IP`` with the server IP.
Do not bypass certificate verification for a deployment acceptance check.

Operation and backups
-------------------------

Application commands run from ``publication-site/pubhub`` and retain the same
project name and override. To stop, resume, or restart:

.. code-block:: bash

   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml stop
   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml start
   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml restart

Run the HTTPS checks and verify your administrator login after resuming. Named
volumes retain PostgreSQL data, backups, and Django logs across restarts or
``down``/``up``. Do not delete volumes as routine maintenance. The production
Compose files have no restart policy; arrange service startup after host reboots
and confirm availability rather than assuming automatic recovery.

For an application update, review the migration guide and take a backup first.
From ``publication-site/pubhub``, after updating your checkout:

.. code-block:: bash

   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml build
   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml stop django
   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml run --rm django python manage.py migrate
   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml up -d

Repeat the launch verification. Source and dependency changes require rebuilding;
environment changes require recreation (``up -d --force-recreate``). To inspect
application request logs stored in the volume:

.. code-block:: bash

   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml exec django tail -n 100 /var/log/django/publications-site.log

For a database backup, with PostgreSQL running, from ``publication-site/pubhub``:

.. code-block:: bash

   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml exec postgres backup
   mkdir -p backups
   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml cp postgres:/backups/. ./backups/
   gzip -t backups/backup_*.sql.gz

The backup command reports its filename; ``gzip -t`` should exit successfully.
Copy backups to protected off-host storage and rehearse a restore using the
migration helper documentation. The backup volume alone is not an off-host
backup. A live ``pg_dump`` is a consistent database snapshot; migration cutovers
require stopping all writers as described in the migration guide. Back up your
environment, overrides, and certificates separately.

Proxy commands run from ``publication-site/traefik``:

.. code-block:: bash

   docker compose -p traefik -f docker-compose.prod.yml -f compose.deployment.yml logs --tail=100 traefik
   docker compose -p traefik -f docker-compose.prod.yml -f compose.deployment.yml exec traefik tail -n 100 /var/log/traefik/access.log
   docker compose -p traefik -f docker-compose.prod.yml -f compose.deployment.yml stop
   docker compose -p traefik -f docker-compose.prod.yml -f compose.deployment.yml start

After replacing renewed certificate files, restart Traefik with the same flags
and ``restart``. After changing ``traefik/.env`` or its templates, use the same
flags with ``up --build -d``. Recheck HTTPS and the served certificate. Stop the
application first if removing the proxy stack: its external network is shared.
