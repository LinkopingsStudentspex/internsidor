from django.db import models
from django.conf import settings
from django.utils.http import urlencode

def logout_url(request):
    return settings.LOGOUT_REDIRECT_URL + '?' + urlencode({'redirect_uri': request.build_absolute_uri('/')})