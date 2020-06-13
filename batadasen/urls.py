from django.urls import path, include
from django.conf.urls import url

from . import views
from . import models

app_name= 'batadasen'
urlpatterns = [
    path('activate', views.activation_view, name='activate'),
    path('email_lists/', views.EmailListListView.as_view()),
    path('email_lists/<str:alias>/', views.EmailListDetailView.as_view(), name='emaillist_detail'),
    path('minsida', views.PersonSelfView.as_view(), name='person_self'),
    path('persons/<int:pk>/', views.PersonDetailView.as_view(), name='person_detail'),
    path('productions/', views.ProductionListView.as_view(), name='production_list'),
    path('productions/<int:pk>/', views.ProductionDetailView.as_view(), name='production_detail'),
    path('api/users', views.UserList.as_view()),
    path('api/users_count', views.user_count)
]