# Publication Hub

Publication Hub is a publication management site for groups and organizations that produce more publications than can be managed by hand.

## Native desktop development (no Docker)

This path uses SQLite and needs only a supported Python installation. It creates an
empty local schema; production data is not included.

```bash
cd pubhub
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/>. The local SQLite database is created as
`pubhub/local.sqlite3` and is ignored by Git. Use Django management commands or a
separately supplied data dump when data is needed.

## Docker development

Docker Compose continues to use PostgreSQL and the `config.settings.docker`
settings module:

```bash
cd pubhub
docker compose up --build
```

[Documentation can be found here](https://aims-group.github.io/publication-site/)
