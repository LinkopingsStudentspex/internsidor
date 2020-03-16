from django.urls import path, include
from django.conf.urls import url
from . import views

urlpatterns = [
    path('activate', views.activation_view),
    path('email_list/<str:alias>', views.view_recipients)
]