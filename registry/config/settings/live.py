from .staging import *  # noqa

ALLOWED_HOSTS = ['x.x.x']

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5)  # noqa
}
