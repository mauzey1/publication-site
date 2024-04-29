import os
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'publisher.processors.nav_options',
                'publisher.processors.pending_dois'
            ],
        },
    },
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DATABASES = {
  'default': {
      'ENGINE': 'django.db.backends.postgresql',
      'NAME': os.environ.get("POSTGRES_DB"),
      'USER': os.environ.get("POSTGRES_USER"),             # Not used with sqlite3.
      'PASSWORD': os.environ.get("POSTGRES_PASSWORD"),         # Not used with sqlite3.
      'HOST': os.environ.get("POSTGRES_HOST"),             # Not used with sqlite3.
      'PORT': os.environ.get("POSTGRES_PORT"),             # Not used with sqlite3.
  }
}

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", default='29l93ms9m32390#20-z!32ad38')

# Google's recaptcha. Refer to the recaptcha web site for this key https://www.google.com/recaptcha/intro/
RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY", default='')
RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY", default='')

# Email values must be set for password recovery to function
EMAIL_HOST = os.environ.get("EMAIL_HOST", default='localhost')
EMAIL_PORT = os.environ.get("EMAIL_PORT", default=1025)

# os.environ["REQUESTS_CA_BUNDLE"] = "/absolute/path/to/certfile.crt"  
# Path to the .crt file. 
# Used if the server is behind a corporate firewall that intercepts ssl
# This can be set to "" (empty string) if your server is not behind one of these annoying firewalls

# Django Admin URL regex.
ADMIN_URL = os.environ.get("DJANGO_ADMIN_URL")