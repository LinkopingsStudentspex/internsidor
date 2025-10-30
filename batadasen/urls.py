from django.urls import path

from . import views

app_name = "batadasen"
urlpatterns = [
    path("activate", views.activation_view, name="activate"),
    path("email_lists/", views.email_list_filter, name="emaillist_list"),
    path(
        "email_lists/<str:alias>/",
        views.EmailListDetailView.as_view(),
        name="emaillist_detail",
    ),
    path("settings/", views.PersonSelfView.as_view(), name="person_settings"),
    path(
        "settings/extra_email/",
        views.ExtraEmailView.as_view(),
        name="person_extra_email",
    ),
    path("persons/", views.PersonListView.as_view(), name="person_list"),
    path("persons/<int:pk>/", views.PersonDetailView.as_view(), name="person_detail"),
    path("hundraklubben/", views.Club100.as_view(), name="hundraklubben"),
    path("medals/", views.Medals.as_view(), name="medals"),
    path("productions/", views.ProductionListView.as_view(), name="production_list"),
    path(
        "productions/<int:pk>/",
        views.ProductionDetailView.as_view(),
        name="production_detail",
    ),
    path(
        "productions/<int:pk>/<str:group_shortname>/",
        views.ProductionGroupDetailView.as_view(),
        name="production_group_detail",
    ),
    path(
        "association/",
        views.AssociationYearListView.as_view(),
        name="associationyear_list",
    ),
    path(
        "association/<int:pk>/",
        views.AssociationYearDetailView.as_view(),
        name="associationyear_detail",
    ),
    path(
        "association/<int:pk>/<str:group_shortname>/",
        views.AssociationYearGroupDetailView.as_view(),
        name="associationyear_group_detail",
    ),
    path("statistics/", views.StatisticsView.as_view(), name="statistics"),
    path("api/users", views.UserList.as_view()),
    path("api/users_count", views.user_count),
    path("no_admin/", views.no_admin_view, name="no_admin"),
    path("", views.index_view, name="index"),
]
