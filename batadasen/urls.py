from django.urls import path, include
from django.conf.urls import url
from . import views

app_name= 'batadasen'
urlpatterns = [
    path('activate', views.activation_view, name='activate'),
    path('email_list/<str:alias>', views.view_recipients),
    path('minsida', views.person_self_view, name='person_self'),
]