# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
from decouple import config
from unipath import Path
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).parent
CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_1122')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True#config('DEBUG', default=True, cast=bool)

# load production server from .env
ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1', config('SERVER', default='127.0.0.1')]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'colorfield',
    'widget_tweaks',
    'bootstrap_modal_forms',
    'mathfilters',
    'rest_framework',
    'corsheaders',
    'django_extensions',

    'authentication',
    'beachhandball_app',  # Enable the inner app 
    #'debug_toolbar'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsPostCsrfMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
]
INTERNAL_IPS = [
    # ...
    '127.0.0.1',
    'beach-tournament-organizer.herokuapp.com',
    'german-beach-open.app',
    'tournament-organizer-app.onrender.com',
    'skybeach-services.de',
]
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = [
        'http://127.0.0.1:8000',
        'http://127.0.0.1:5005',
        'http://german-beach-open.app',
        'skybeach-services.de',
    ]

ROOT_URLCONF = 'core.urls'
LOGIN_REDIRECT_URL = "login"   # Route defined in app/urls.py
LOGOUT_REDIRECT_URL = "login"  # Route defined in app/urls.py
TEMPLATE_DIR = os.path.join(CORE_DIR, "core/templates")  # ROOT dir for templates

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [TEMPLATE_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "environment": "core.jinja2.environment",
            'context_processors': [
                'django.contrib.messages.context_processors.messages',
            ],
        }
    },

    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
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

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    #'default': {
    #    'ENGINE': 'django.db.backends.sqlite3',
    #    'NAME'  : 'db.sqlite3',
    #}
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': os.path.join(BASE_DIR, 'database_config.cnf'),
            "init_command": "SET foreign_key_checks = 0;",
        },
        'CONN_MAX_AGE ': 0,
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True

#############################################################
# SRC: https://devcenter.heroku.com/articles/django-assets

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(CORE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(CORE_DIR, 'core/static'),
)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(CORE_DIR, 'media')

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

#############################################################
#############################################################

SWS_BASE_URL = 'https://vmd99610.contaboserver.net/sws'
#SWS_BASE_URL = 'https://euve268544.serverprofi24.de:3060'
#IWS_BASE_URL = 'https://euve268544.serverprofi24.de:3080'

#SWS_BASE_URL = 'https://german-beach-open.app:3060'
#SWS_BASE_URL = 'https://karacho-beach-tournament.de:3060'
IWS_BASE_URL = 'https://vmd99610.contaboserver.net/iws'
SWS_VERIFY_SSL = True


GAME_REPORT_DIR = os.path.join(BASE_DIR, 'report')

#if 'REDIS_URL' in os.environ:
#    REDIS_URL = os.environ['REDIS_URL']
#else:
REDIS_URL = 'redis://default:DCAc3YQZML0VJEIr48oOeHXP4Ya5srL1@redis-18486.c293.eu-central-1-1.ec2.cloud.redislabs.com:18486'
REDIS_URL = None
if REDIS_URL is not None:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.environ.get('REDIS_URL'),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }


MQTT_BROKER='skybeach-services.de'
MQTT_PORT=8083

BROKER_URL = REDIS_URL
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_TASK_ALWAYS_EAGER  = False

#CELERY_ACCEPT_CONTENT = ['application/json']
#CELERY_TASK_SERIALIZER = 'json'
#CELERY_RESULT_SERIALIZER = 'json'
#CELERY_TIMEZONE = 'Africa/Nairobi'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}
