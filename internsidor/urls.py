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
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include, reverse
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.views.generic.base import View

class CustomLogin(View):
    def get(self, request, **kwargs):
        return HttpResponseRedirect(
            reverse('oidc_authentication_init') + (
                '?next={}'.format(request.GET['next']) if 'next' in request.GET else ''
            )
        )

if 'mozilla_django_oidc' in settings.INSTALLED_APPS:
    urlpatterns = [
        path('admin/login/', CustomLogin.as_view()),
        # path('admin/logout/', lambda request: redirect('oidc_logout', permanent=False)),
        path('admin/', admin.site.urls),
        path('batadasen/', include('batadasen.urls')),
        path('oidc/', include('mozilla_django_oidc.urls'))
    ]
else:
    urlpatterns = [
        path('admin/', admin.site.urls),
        path('batadasen/', include('batadasen.urls')),

        # A simple login view for dev setups that don't have keycloak available
        path('login/', auth_views.LoginView.as_view(template_name='batadasen/dev_login.html'), name='login'),

        # Fake the oidc_logout url to make the logout button happy
        path('logout/', auth_views.LogoutView.as_view(), name='oidc_logout'),
    ]



