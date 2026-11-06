Production deployment
=====================

Deploy a new Publication Hub installation on a Linux server with PostgreSQL,
Gunicorn, and Traefik. Traefik handles HTTPS using a certificate you provide.
Follow the numbered steps in order, then use the maintenance instructions to
manage the running site.

Step 1: Check the prerequisites
-------------------------------

This procedure creates a **new installation** on a Linux host with Git, Docker
Engine, Docker Compose v2, Bash, and OpenSSL. Run these checks from any directory:

.. code-block:: bash

   docker info
   docker compose version
   openssl version

All three commands should succeed. You also need:

* A domain such as ``publications.example.org`` with DNS pointing to the host.
* An existing TLS certificate chain and matching private key for that domain.
  Traefik does not obtain or renew certificates in this configuration.
* Ports 80 and 443 available and reachable by your users. The application Compose
  file also publishes port 5000; restrict external access to it with host/network
  rules that cover Docker-published ports so requests enter through Traefik.
* A location for off-host database backups.

Serve the site at the domain root, such as ``https://publications.example.org/``,
and leave ``DOMAIN_SUBDIRECTORY`` empty. The bundled proxy uses HTTP Strict
Transport Security (HSTS) to require HTTPS for the domain and its subdomains.
Make sure those subdomains support HTTPS as well.

For an existing database, read the migration guide linked from
:doc:`Getting Started` before proceeding.

Step 2: Download the code
-------------------------

On the server, start in the directory where you want to store the repository:

.. code-block:: bash

   git clone https://github.com/aims-group/publication-site.git
   cd publication-site

Step 3: Create the application environment file
-----------------------------------------------

Generate two separate secrets. Each command prints 32 random bytes as 64
hexadecimal characters; it does not save the value. Copy the first output for
the Django secret key and the second for the PostgreSQL password. Keep both
outputs private:

.. code-block:: bash

   openssl rand -hex 32

Save that output as the Django secret key. Then generate the database password:

.. code-block:: bash

   openssl rand -hex 32

From the checkout root, copy the tracked example file:

.. code-block:: bash

   cp pubhub/.envs/.prod.env.example pubhub/.envs/.prod.env

If ``pubhub/.envs/.prod.env`` already exists, review it instead of overwriting
it. Edit the copied file: paste the first random output into
``DJANGO_SECRET_KEY`` and the second into ``POSTGRES_PASSWORD``, replacing the
placeholders. Replace the example domain with your domain in
``DJANGO_ALLOWED_HOSTS`` and ``DEFAULT_FROM_EMAIL``.

``DJANGO_ALLOWED_HOSTS`` is a comma-separated list of hostnames without schemes
or paths. The explicit log path is required: the image runs as a non-root user
and provides a writable ``/var/log/django`` directory. The default log path
outside that directory is not writable. Registration and password reset need
additional service configuration; see :doc:`configuration`.

From the checkout root, protect the environment file:

.. code-block:: bash

   chmod 600 pubhub/.envs/.prod.env

Git ignores this file. Compose loads its values when it creates the containers.
Keep a private backup of the file. If you change ``POSTGRES_PASSWORD`` later,
you must also update the password in PostgreSQL; editing the file alone does
not change an existing database account.

Step 4: Connect Django to the database network
----------------------------------------------

From the checkout root, create ``pubhub/compose.deployment.yml``:

.. code-block:: yaml

   services:
     django:
       networks:
         - default
         - traefik_default
   networks:
     default: {}

The production Compose file connects Django to the proxy network and PostgreSQL
to the application network. This additional Compose file connects Django to
both networks so it can reach the database. Every application command below
includes both files. Keep ``compose.deployment.yml`` with your deployment
configuration.

Step 5: Install the TLS certificate
-----------------------------------

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

Step 6: Configure Traefik
-------------------------

From the repository root (``publication-site``), copy the tracked Traefik
example. If ``traefik/.env`` already exists, review it instead of overwriting
it:

.. code-block:: bash

   cp traefik/.env.example traefik/.env

Edit ``traefik/.env`` and replace the example domain with your domain.

Create ``traefik/compose.deployment.yml``:

.. code-block:: yaml

   services:
     traefik:
       volumes:
         - /etc/publication-hub/tls:/etc/traefik/ssl:ro

Compose replaces the original volume mount at ``/etc/traefik/ssl`` with this
read-only bind mount. Traefik expects the filenames ``cert.pem`` and ``key.pem``.
Traefik's domain configuration is included in the image during the build.

Step 7: Build and start Traefik
-------------------------------

From the repository root:

.. code-block:: bash

   cd traefik
   docker compose -p traefik -f docker-compose.prod.yml -f compose.deployment.yml config --quiet

If validation succeeds, build and start the proxy:

.. code-block:: bash

   docker compose -p traefik -f docker-compose.prod.yml -f compose.deployment.yml up --build -d

Confirm that its network exists:

.. code-block:: bash

   docker network inspect traefik_default --format '{{.Name}}'

The final command should print ``traefik_default``. Always use ``-p traefik``:
it creates the external network expected by the application. Until Django starts,
the proxy may return a gateway error.

Step 8: Build the application and create the database
-----------------------------------------------------

From ``publication-site/traefik``, enter the application directory:

.. code-block:: bash

   cd ../pubhub
   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml config --quiet

If validation succeeds, build the application and database images:

.. code-block:: bash

   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml build

Start PostgreSQL:

.. code-block:: bash

   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml up -d postgres

Create the database tables:

.. code-block:: bash

   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml run --rm django python manage.py migrate

After migrations finish, create the administrator account. Run this command by
itself and answer its prompts before continuing:

.. code-block:: bash

   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml run --rm django python manage.py createsuperuser

The application waits for PostgreSQL to accept connections before running each
management command. Migrations should finish without errors. When prompted,
enter a username, email address, and password for the administrator account.

Step 9: Load optional climate metadata
--------------------------------------

To add the bundled climate project tags and journal names, run this command
from ``publication-site/pubhub``. Skip this step if you plan to create your own
metadata through the administrator interface.

.. code-block:: bash

   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml run --rm django python manage.py initialize

Initialization does not create publication records. See :ref:`metadata` for
details.

Step 10: Start the application
------------------------------

Still in ``publication-site/pubhub``:

.. code-block:: bash

   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml up -d

Startup collects static files and starts Gunicorn on port 5000. Database
migrations must be run separately, as in step 8.

Step 11: Verify the deployment
------------------------------

From ``publication-site/pubhub``, check the application and database migrations,
then inspect the service status and recent logs:

.. code-block:: bash

   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml exec django python manage.py check
   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml exec django python manage.py migrate --check
   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml ps
   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml logs --tail=100 django postgres

The checks should succeed and both services should remain running. From any
directory, check HTTP and HTTPS access, replacing the example domain with yours:

.. code-block:: bash

   curl -sS -o /dev/null -w '%{http_code}\n' http://publications.example.org/
   curl -sS -o /dev/null -w '%{http_code}\n' https://publications.example.org/
   curl -sS -o /dev/null -w '%{http_code}\n' https://publications.example.org/static/uswds/css/uswds.min.css

The HTTP request should redirect to HTTPS. Both HTTPS requests should return
HTTP 200 with a trusted certificate. Open your site's ``/admin/`` page and sign
in with the administrator account you created in step 8. Configure
:ref:`recaptcha` and :ref:`email` before using public registration or password
reset.

The homepage accepts only GET requests. Other request methods return HTTP 405,
so use the commands above to check its availability.

To test before DNS changes, use ``curl --resolve publications.example.org:443:HOST_IP
-sS -o /dev/null -w '%{http_code}\n' https://publications.example.org/``, replacing ``HOST_IP`` with the server IP.
Do not bypass certificate verification for a deployment acceptance check.

Stop and resume
---------------

Application commands run from ``publication-site/pubhub`` and retain the same
project name and both Compose files. To stop the application stack:

.. code-block:: bash

   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml stop

To start it again:

.. code-block:: bash

   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml start

Run the HTTPS checks and verify your administrator login after resuming. Named
volumes retain PostgreSQL data, backups, and Django logs across restarts or
``down``/``up``. Do not delete volumes as routine maintenance. The production
Compose files have no restart policy; arrange service startup after host reboots
and verify that the site is available after each reboot.

Update the application
----------------------

1. Review the migration guide linked from :doc:`Getting Started`.
2. Back up the database using the instructions below.
3. Update your repository checkout to the version you intend to deploy.
4. From ``publication-site/pubhub``, rebuild the image, stop Django, apply
   migrations, and start the application:

   .. code-block:: bash

      docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml build
      docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml stop django
      docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml run --rm django python manage.py migrate
      docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml up -d

Repeat the checks in step 11. Code and dependency changes require rebuilding the
image; environment changes require recreating containers with
``up -d --force-recreate`` and the same project name and Compose files. To inspect
application request logs stored in the volume:

.. code-block:: bash

   docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml exec django tail -n 100 /var/log/django/publications-site.log

Back up the database
--------------------

1. Make sure PostgreSQL is running.
2. From ``publication-site/pubhub``, create a backup, copy it to the host, and
   check that the compressed files can be read:

   .. code-block:: bash

      docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml exec postgres backup
      mkdir -p backups
      docker compose -p pubhub -f docker-compose.prod.yml -f compose.deployment.yml cp postgres:/backups/. ./backups/
      gzip -t backups/backup_*.sql.gz

   The backup command reports its filename. ``gzip -t`` should finish without
   errors.

3. Copy the backup files to protected storage on another host.
4. Rehearse a restore using the migration helper documentation linked from
   :doc:`Getting Started`.
5. Back up your environment files, Compose overrides, and certificates separately.

A live ``pg_dump`` produces a consistent database snapshot. For a migration
cutover, stop all processes that write to the database as described in the
migration guide.

Maintain Traefik
----------------

Proxy commands run from ``publication-site/traefik``:

.. code-block:: bash

   docker compose -p traefik -f docker-compose.prod.yml -f compose.deployment.yml logs --tail=100 traefik
   docker compose -p traefik -f docker-compose.prod.yml -f compose.deployment.yml exec traefik tail -n 100 /var/log/traefik/access.log

To stop the proxy:

.. code-block:: bash

   docker compose -p traefik -f docker-compose.prod.yml -f compose.deployment.yml stop

To start it again:

.. code-block:: bash

   docker compose -p traefik -f docker-compose.prod.yml -f compose.deployment.yml start

After copying renewed certificates to the paths in step 5, restart Traefik:

.. code-block:: bash

   docker compose -p traefik -f docker-compose.prod.yml -f compose.deployment.yml restart

After changing ``traefik/.env`` or its templates, rebuild and recreate the proxy:

.. code-block:: bash

   docker compose -p traefik -f docker-compose.prod.yml -f compose.deployment.yml up --build -d

Repeat the HTTPS checks in step 11 and confirm that the served certificate is
valid. Before removing the proxy stack, stop and remove the application
containers so they no longer use the shared ``traefik_default`` network.
