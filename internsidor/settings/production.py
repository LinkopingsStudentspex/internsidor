from .base import *

AUTHENTICATION_BACKENDS = [
    'batadasen.backends.BatadasenOIDCBackend',
    'django.contrib.auth.backends.ModelBackend'
]

INSTALLED_APPS.append('mozilla_django_oidc')

OIDC_CREATE_USER = False
OIDC_RP_SIGN_ALGO = 'RS256'

OIDC_OP_LOGOUT_URL_METHOD = 'batadasen.provider_logout'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

LOGIN_URL = '/oidc/authenticate/'

try: 
    from .local import *
except ImportError:
    pass