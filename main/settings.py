from .localsettings import (
    BASE_DIR, SECRET_KEY, ALLOWED_HOSTS, DATABASES, STATIC_URL, STATIC_ROOT,
    MEDIA_ROOT, MEDIA_URL, ACSERVERROOT, ACSERVERWRAPPERROOT, ACSERVEREXE,
    ACWRAPPEREXE, DEFAULT_ADMIN_PASSWORD, ABSOLUTE_URL, STEAM_WEB_API,
    DEBUG, CSRF_TRUSTED_ORIGINS, LOG_FILENAME, JOIN_IP, JOIN_PORT)
import os


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cars',
    'races',
    'tracks',
    'drivers',
    'django_extensions',
    'adhoc',
    'main',
    'bootstrap5',
    'easy_thumbnails',
    'django_markup',
    'django_bootstrap_icons',
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

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'main.wsgi.application'


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

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_FILENAME,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# easy thumbnails

THUMBNAIL_ALIASES = {
    'races.RaceSetup.image': {
        'micro': {'size': (104, 44), 'crop': True},
        'small': {'size': (416, 176), 'crop': True},
    },
}

# bootstrap icons?
BS_ICONS_BASE_URL = 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.9.0/'
BS_ICONS_CACHE = os.path.join(STATIC_ROOT, 'icon_cache')

# Caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'acracerscache',
    }
}
