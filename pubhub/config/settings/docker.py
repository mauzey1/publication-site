"""Settings for the local Docker Compose development environment."""

import os

from .base import *


DEBUG = True
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "unsafe-docker-development-key")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "postgres"),
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres"),
        "HOST": os.environ.get("POSTGRES_HOST", "postgres"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

INSTALLED_APPS = ["whitenoise.runserver_nostatic"] + INSTALLED_APPS
