"""
Django settings for HMS project.
"""

from pathlib import Path
from decouple import config

##########################
# BASE DIRECTORY
##########################

BASE_DIR = Path(__file__).resolve().parent.parent


##########################
# SECURITY SETTINGS
##########################

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')


##########################
# APPLICATION DEFINITION
##########################

INSTALLED_APPS = [
    'jazzmin',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'accounts',
    'guests',
    'rooms',
    'bookings',
    'staff',
    'referrals',
    'billing',
    'reports',
    'core',
]


##########################
# MIDDLEWARE
##########################

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


##########################
# URL CONFIGURATION
##########################

ROOT_URLCONF = 'HMS.urls'


##########################
# TEMPLATES CONFIGURATION
##########################

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'Frontend'],
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


##########################
# WSGI / ASGI
##########################

WSGI_APPLICATION = 'HMS.wsgi.application'
ASGI_APPLICATION = 'HMS.asgi.application'


##########################
# DATABASE CONFIGURATION
##########################

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}


##########################
# PASSWORD VALIDATION
##########################

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


##########################
# INTERNATIONALIZATION
##########################

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kathmandu'
USE_I18N = True
USE_TZ = True


##########################
# STATIC FILES CONFIG
##########################

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'


##########################
# MEDIA FILES CONFIG
##########################

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


##########################
# DEFAULT PRIMARY KEY
##########################

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


##########################
# EMAIL SETTINGS
##########################

EMAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')


##########################
# JAZZMIN ADMIN SETTINGS
##########################

JAZZMIN_SETTINGS = {
    "site_title": "HMS Admin",
    "site_header": "Hotel Management System",
    "site_brand": "HMS",
    "welcome_sign": "Welcome to HMS Admin Panel",
    "copyright": "HMS",
    "show_sidebar": True,
    "navigation_expanded": True,
}