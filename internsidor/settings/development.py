from .base import * 

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1h2i9=^yld5y6q$f1_qkjj23@ytmp-2!i)m@bvr-6$)fa#*149'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

AUTHENTICATION_BACKENDS = [
   'django.contrib.auth.backends.ModelBackend'
]

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LOGIN_URL = 'login'

EMAIL_DOMAIN = 'localhost'

try: 
    from .local import *
except ImportError:
    pass