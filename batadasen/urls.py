from django.urls import path, include
from django.conf.urls import url
from . import views

app_name= 'batadasen'
urlpatterns = [
    path('activate', views.activation_view, name='activate'),
    path('email_lists/', views.EmailListListView.as_view()),
    path('email_lists/<str:alias>/', views.EmailListDetailView.as_view(), name='emaillist_detail'),
    path('minsida', views.PersonUpdateView.as_view(), name='person_self'),
    path('persons/<int:pk>/', views.PersonDetailView.as_view(), name='person_detail')
]