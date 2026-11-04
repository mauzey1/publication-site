# Publication Hub

Publication Hub helps groups and organizations catalog, search, and manage their
publications, with project tags and bundled climate science metadata.

Choose a setup path:

- [Native development](https://aims-group.github.io/publication-site/html/native-development.html): Python 3.12 and SQLite; the quickest way to work locally.
- [Docker development](https://aims-group.github.io/publication-site/html/docker-development.html): Docker Compose and PostgreSQL, with automatic metadata initialization.
- [Production deployment](https://aims-group.github.io/publication-site/html/production.html): a fresh Linux deployment with PostgreSQL, Gunicorn, Traefik, and HTTPS.

## Native quick start

Prerequisites: Git, Python 3.12, and Bash (macOS, Linux, or Windows through WSL).
Run from the directory where you keep your checkouts:

```bash
git clone https://github.com/aims-group/publication-site.git
cd publication-site/pubhub
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
unset DJANGO_SETTINGS_MODULE
python manage.py migrate
```

Create an administrator account. Run this command by itself and answer its
prompts before continuing:

```bash
python manage.py createsuperuser
```

Start the server and leave this terminal open:

```bash
python manage.py runserver
```

Open <http://127.0.0.1:8000/> and sign in at <http://127.0.0.1:8000/admin/>.
In another terminal, `curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/` should return HTTP 200.
The database is `pubhub/local.sqlite3` (ignored by Git); initially it contains no
publications. Optional `python manage.py initialize` adds bundled project tags
and journal names, not publications.

See the [full guide](https://aims-group.github.io/publication-site/) for environment
files, configuration, troubleshooting, and operating commands. Existing deployments
should follow the [migration guide](pubhub/scripts/migration/README.md).
Documentation sources and [build instructions](docs/README.md) live in `docs/`.
