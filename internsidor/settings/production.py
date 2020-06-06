from .base import *

AUTHENTICATION_BACKENDS = [
    'batadasen.backends.BatadasenOIDCBackend',
    # 'django.contrib.auth.backends.ModelBackend'
]

INSTALLED_APPS.append('mozilla_django_oidc')

# This will cause ID tokens of users to expire after a time,
# causing the browser to silently re-auth with the OIDC provider in the background.
# Otherwise, inactivated users could still have an active session in
# django for long time.
MIDDLEWARE.append('mozilla_django_oidc.middleware.SessionRefresh')

OIDC_CREATE_USER = False
OIDC_RP_SIGN_ALGO = 'RS256'

OIDC_OP_LOGOUT_URL_METHOD = 'batadasen.provider_logout'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

LOGIN_URL = '/oidc/authenticate/'

try: 
    from .local import *
except ImportError:
    pass