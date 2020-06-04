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

# Load OIDC client configuration.
# Following variables must be defined in 
# oidc_client_info.py

# OIDC_RP_CLIENT_ID
# OIDC_RP_CLIENT_SECRET
# OIDC_OP_AUTHORIZATION_ENDPOINT
# OIDC_OP_TOKEN_ENDPOINT
# OIDC_OP_USER_ENDPOINT
# OIDC_OP_JWKS_ENDPOINT
try: 
    from .oidc_client_info import *
except ImportError:
    pass

try: 
    from .local import *
except ImportError:
    pass