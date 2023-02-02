from .base import *  # noqa

ALLOWED_HOSTS = ['staging.x.x.x']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME'),  # noqa
        'USER': config('DB_USER'),  # noqa
        'PASSWORD': config('DB_PASS'),  # noqa
        'HOST': 'localhost',
        'PORT': '',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379',
    }
}

STATIC_ROOT = BASE_DIR / "static"  # noqa

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=200)  # noqa
}
