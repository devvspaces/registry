import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-dx7-#u^_s7c$xvx-b7jukr&lrpsz+@u5b#-069v-d1$iap%7cp'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_yasg',
    
    'rest_framework',
    "corsheaders",
    'authentication',
    'project_api_key',
]


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTTokenUserAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'authentication.pagination.CustomPagination',
}

API_KEY_HEADER = "HTTP_BEARER_API_KEY"
API_SEC_KEY_HEADER = "HTTP_BEARER_SEC_API_KEY"


MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# AUTHENTICATION_BACKENDS = (
#         'django.contrib.auth.backends.RemoteUserBackend',
#         'django.contrib.auth.backends.ModelBackend',
# )

CORS_ALLOWED_ORIGINS = [
    # "http://127.0.0.1:8000",
]

from corsheaders.defaults import default_headers

CORS_ALLOW_HEADERS = list(default_headers) + [
    "Bearer-Api-Key",
    "Bearer-Sec-Api-Key",
]

ROOT_URLCONF = 'registry.urls'
AUTH_USER_MODEL = 'authentication.User'

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

WSGI_APPLICATION = 'registry.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


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


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


EMAIL_BACKEND= 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST="smtp.gmail.com"
EMAIL_PORT= 587
EMAIL_USE_TLS= True
EMAIL_HOST_USER = "netrobeweb@gmail.com"
EMAIL_HOST_PASSWORD = "wpcgtxfwmiqnlbwv"
# Custom user defined mail username
DEFAULT_FROM_EMAIL = "info@cryptopython.com"
DEFAULT_COMPANY_EMAIL = "info@cryptopython.com"


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'basic': {
            'handlers': ['basic_h'],
            'level': 'DEBUG',
        },
        'basic.error': {
            'handlers': ['basic_e'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
    'handlers': {
        'basic_h': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': './logs/debug.log',
            'formatter' : 'simple',
        },
        'basic_e': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': './logs/error.log',
            'formatter' : 'simple',
        },
    },
    'formatters':{
        'simple': {
            'format': '{levelname} : {asctime} : {message}',
            'style': '{',
        }
    }
}
TWILIO_ACCOUNT_SID = 'ACa903f93b979c86ca657709393ace7336'
TWILIO_AUTH_TOKEN = '831c9fb4546fcd2018ec9c9c866bf415'
