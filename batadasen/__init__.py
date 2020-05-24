from django.conf import settings
from django.utils.http import urlencode

def provider_logout(request):
    logout_url = settings.OIDC_OP_LOGOUT_ENDPOINT
    return_to_url = request.build_absolute_uri(settings.LOGOUT_REDIRECT_URL)
    return "{}?{}".format(logout_url, urlencode({'redirect_uri': return_to_url}))