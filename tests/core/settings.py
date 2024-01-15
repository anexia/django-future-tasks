"""
Django settings for "tests" project which assures the functionality of the "django-future-tasks" package
(https://github.com/anexia/django-future-tasks).
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "H0&?S3ZyJVDoLdvzU6OhQ1i?rabJ7Pwd3#2NF.ge7NgWrRQKX$utvpd!4MPL"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_future_tasks",
    "cronfield",
    "testapp",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Vienna"

USE_I18N = True

USE_L10N = True

USE_TZ = True

FUTURE_TASK_TYPE_ONE = "task_one"
FUTURE_TASK_TYPE_TWO = "task_two"
FUTURE_TASK_TYPE_ERROR = "task_error"
FUTURE_TASK_TYPE_INTERRUPTION = "task_interruption"

FUTURE_TASK_TYPES = (
    (FUTURE_TASK_TYPE_ONE, "Task 1"),
    (FUTURE_TASK_TYPE_TWO, "Task 2"),
    (FUTURE_TASK_TYPE_ERROR, "Task Error"),
    (FUTURE_TASK_TYPE_INTERRUPTION, "Task Interruption"),
)

STATIC_URL = "/static/"
ROOT_URLCONF = "core.urls"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
