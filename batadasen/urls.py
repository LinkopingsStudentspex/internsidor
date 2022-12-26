from django.urls import path, include

from . import views
from . import models

app_name= 'batadasen'
urlpatterns = [
    path('activate', views.activation_view, name='activate'),
    path('email_lists/', views.email_list_filter, name='emaillist_list'),
    path('email_lists/<str:alias>/', views.EmailListDetailView.as_view(), name='emaillist_detail'),
    path('settings/', views.PersonSelfView.as_view(), name='person_settings'),
    path('settings/extra_email/', views.ExtraEmailView.as_view(), name='person_extra_email'),
    path('persons/<int:pk>/', views.PersonDetailView.as_view(), name='person_detail'),
    path('productions/', views.ProductionListView.as_view(), name='production_list'),
    path('productions/<int:pk>/', views.ProductionDetailView.as_view(), name='production_detail'),
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/add', views.CreateEventView.as_view(), name='event_add'),
    path('events/<int:pk>', views.EventView.as_view(), name='event_detail'),
    path('events/<int:pk>/edit', views.EditEventView.as_view(), name='event_edit'),
    path('api/users', views.UserList.as_view()),
    path('api/users_count', views.user_count),
    path('no_admin/', views.no_admin_view, name='no_admin'),
    path('', views.index_view, name='index')
]
