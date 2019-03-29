"""
Django settings for NeutronServer project.

Generated by 'django-admin startproject' using Django 2.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""
import posixpath
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

secret_dir = os.getenv("SECRETS_LOCATION")
use_secrets = os.path.isdir(str(secret_dir))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
if use_secrets:
    SECRET_KEY = open(secret_dir+"/secret_key", "r").read().strip()
else:
    SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# If we're using secrets, we are in production, debugging is off
DEBUG = not use_secrets

ALLOWED_HOSTS = []
if use_secrets:
    # Allowed hosts are listed in the filter_host middleware
    ALLOWED_HOSTS.append('*')

# Application definition
INSTALLED_APPS = [
    'update_manager.apps.UpdateManagerConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'channels',
]


ASGI_APPLICATION = "NeutronServer.routing.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(os.getenv('REDIS_HOST'), os.getenv('REDIS_PORT'))],
        },
    },
}

if use_secrets:
    log_level = 'WARNING'
else:
    log_level = 'DEBUG'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} [{asctime}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django.server': {
            'handlers': ['console'],
            'level': log_level,
            'propagate': False,
        },
    },
}

MIDDLEWARE = []

if use_secrets:
    MIDDLEWARE.append('NeutronServer.middleware.filter_host.FilterHostMiddleware')

MIDDLEWARE.extend([
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
])

ROOT_URLCONF = 'NeutronServer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'NeutronServer.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

if use_secrets:
    sql_user = open(secret_dir+"/sql_user", "r").read().strip()
    sql_pass = open(secret_dir+"/sql_pass", "r").read().strip()
    DATABASES = {
        'default': {
            'ENGINE': os.getenv('SQL_ENGINE'),
            'NAME': os.getenv('SQL_DATABASE'),
            'USER': sql_user,
            'PASSWORD': sql_pass,
            'HOST': os.getenv('SQL_HOST'),
            'PORT': os.getenv('SQL_PORT'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': os.getenv('SQL_ENGINE'),
            'NAME': os.getenv('SQL_DATABASE'),
            'USER': os.getenv('SQL_USER'),
            'PASSWORD': os.getenv('SQL_PASSWORD'),
            'HOST': os.getenv('SQL_HOST'),
            'PORT': os.getenv('SQL_PORT'),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/mediafiles/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# Temporary
VERSION_CONTROL_PACKAGES = '/download/version_control/'
VERSION_CONTROL_ROOT = os.path.join(BASE_DIR, 'update_packages')

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login'