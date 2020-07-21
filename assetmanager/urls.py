from django.urls import path, include
from django.views.generic.base import RedirectView
from assetmanager.views import (
    AssetListView, 
    AssetDetailView, 
    AssetModelDetailView, 
    new_logentry_view,
    new_asset_view,
    new_assetmodel_view,
    new_category_view,
    search_view)


app_name= 'assetmanager'
urlpatterns = [
    path('assets/', AssetListView.as_view(), name='asset_list'),
    path('assets/add/', new_asset_view, name='asset_add'),
    path('assets/search/', search_view, name='asset_search'),
    path('assets/<int:number>/', AssetDetailView.as_view(), name='asset_detail'),
    path('assets/<int:number>/new-log-entry/', new_logentry_view, name='create_log_entry'),
    path('assetmodels/<int:pk>/', AssetModelDetailView.as_view(), name='assetmodel_detail'),
    path('assetmodels/add/', new_assetmodel_view, name='assetmodel_add'),
    path('categories/add/', new_category_view, name='category_add'),
    path('', RedirectView.as_view(pattern_name='asset_list', permanent=False)),
]