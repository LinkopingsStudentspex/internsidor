
from django.urls import path, include, reverse

from showcounter import views

app_name= 'showcounter'
urlpatterns = [
    path('production/<int:number>', views.production, name='production'),
    path('', views.overview, name='overview'),
]