from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'productions', views.ProductionViewSet)

app_name= 'spexflix'
urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.ProductionList.as_view(), name='index'),
    path('productions/<int:pk>', views.ProductionDetail.as_view(), name='production-detail'),
    path('video/<int:pk>', views.VideoDetail.as_view(), name='video-detail'),
]