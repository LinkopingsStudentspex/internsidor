"""internsidor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include, reverse
from django.http import HttpResponse
from django.views.generic.base import TemplateView

from ajax_select import urls as ajax_select_urls

import batadasen
import assetmanager

def auth_check(request):
    """
    Empty response view for use with Nginx auth_request
    """
    if request.user.is_authenticated:
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=401, headers={'WWW-Authenticate': 'Bearer'})

if 'mozilla_django_oidc' in settings.INSTALLED_APPS:
    urlpatterns = [
        # This is a hack to workaround the fact that the admin logout link uses GET but 
        # the mozilla_django_oidc logout page requires a POST request. 
        # The logout_get.html simply instructs the user to logout with the regular logout button.
        path('admin/logout/', TemplateView.as_view(template_name='batadasen/logout_get.html')),

        path('admin/', admin.site.urls),
        path('batadasen/', include('batadasen.urls')),
        path('lissinv/', include('assetmanager.urls')),
        path('showcounter/', include('showcounter.urls')),
        path('spexflix/', include('spexflix.urls')),
        path('ajax_select/', include(ajax_select_urls)),
        path('oidc/', include('mozilla_django_oidc.urls')),
        path('auth_check', auth_check, name='auth-check'),
        path('', batadasen.views.index_view)
    ]
else:
    urlpatterns = [
        path('admin/', admin.site.urls),
        path('batadasen/', include('batadasen.urls')),
        path('lissinv/', include('assetmanager.urls')),
        path('showcounter/', include('showcounter.urls')),
        path('spexflix/', include('spexflix.urls')),
        path('ajax_select/', include(ajax_select_urls)),

        # A simple login view for dev setups that don't have keycloak available
        path('login/', auth_views.LoginView.as_view(template_name='batadasen/dev_login.html'), name='login'),

        # Fake the oidc_logout url to make the logout button happy
        path('logout/', auth_views.LogoutView.as_view(), name='oidc_logout'),
        path('', batadasen.views.index_view)
    ]

    # Used to serve uploaded files during development, NOT FOR PRODUCTION USE
    if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



