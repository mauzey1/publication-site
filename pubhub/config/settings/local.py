import os
from pathlib import Path

from .base import *

# Docker-free development settings. These are deliberately the default used by
# manage.py so a new contributor only needs Python and SQLite to run the site.
DEBUG = True
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", default="unsafe-development-key")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': Path(PROJECT_DIR, 'local.sqlite3'),
    }
}

# WhiteNoise
# ------------------------------------------------------------------------------
# http://whitenoise.evans.io/en/latest/django.html#using-whitenoise-in-development
INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
] + INSTALLED_APPS

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": os.environ.get("DJANGO_LOGGING_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}
