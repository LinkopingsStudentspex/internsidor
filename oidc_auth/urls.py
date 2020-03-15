from django.urls import path, include
from django.conf.urls import url
from . import views

urlpatterns = [
    path('login/', views.login),
    path('users/', views.UserList.as_view()),
    path('users_count/', views.user_count)
]