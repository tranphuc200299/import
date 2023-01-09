"""
Django settings for importCFS project.

Generated by 'django-admin startproject' using Django 4.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
import socket
from pathlib import Path
from decouple import Config, Csv, RepositoryEnv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "main.middleware.exception.middleware.ExceptionHandleMiddleware"
]

ROOT_URLCONF = 'importCFS.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        "DIRS": [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'importCFS.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases


DOTENV_FILE = Path(BASE_DIR).joinpath(".env")  # noqa

env_config = Config(RepositoryEnv(DOTENV_FILE))

SECRET_KEY = env_config("SECRET_KEY", default="abc")

DEBUG = env_config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = env_config("ALLOWED_HOSTS", default="127.0.0.1,localhost,0.0.0.0", cast=Csv())

# ==============================================================================
# DATABASE
# ==============================================================================

DATABASES = {
    "default": {
        "ENGINE": env_config("DB_ENGINE", default="django.db.backends.sqlite3"),
        "NAME": env_config("DB_NAME", default="import_cfs"),
        "USER": env_config("DB_USER"),
        "PASSWORD": env_config("DB_PASSWORD"),
        "HOST": env_config("DB_HOST"),
        "PORT": env_config("DB_PORT"),
    }
}

# ==============================================================================
# SESSION
# ==============================================================================

SESSION_ENGINE = "django.contrib.sessions.backends.file"

# ==============================================================================
# LOGGING
# ==============================================================================

LOG_PATH = Path(BASE_DIR).joinpath("logs")
SERVER_NAME = socket.gethostname()
SERVER_IP = socket.gethostbyname(socket.gethostname())
FILE_NAME_LOG_INFO = SERVER_IP + '_import.log'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'common': {
            'format': '{asctime} {levelname} {name} {module} {lineno} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'info_common': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_PATH, FILE_NAME_LOG_INFO),
            'when': 'midnight',
            'interval': 1,
            'formatter': 'common',
            'backupCount': 30
        },
    },
    'loggers': {
        'django': {
            'handlers': ['info_common'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['info_common'],
            'level': 'INFO',
            'propagate': False,
        },
        'main': {
            'handlers': ['info_common'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'middleware': {
            'handlers': ['info_common'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
