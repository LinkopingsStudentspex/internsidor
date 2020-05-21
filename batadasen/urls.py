from django.urls import path, include
from django.conf.urls import url

from django_filters.views import FilterView

from . import views
from . import models

app_name= 'batadasen'
urlpatterns = [
    path('activate', views.activation_view, name='activate'),
    path('email_lists/', views.EmailListListView.as_view()),
    path('email_lists/<str:alias>/', views.EmailListDetailView.as_view(), name='emaillist_detail'),
    path('minsida', views.PersonUpdateView.as_view(), name='person_self'),
    path('persons/<int:pk>/', views.PersonDetailView.as_view(), name='person_detail'),
    path('persons/', FilterView.as_view(model=models.Person, filterset_fields=('first_name', 'last_name'))),
]