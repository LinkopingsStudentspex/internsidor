from django.views.generic import ListView, DetailView
from rest_framework import viewsets
from . import models, serializers

class ProductionList(ListView):
    model = models.Production
    context_object_name = 'production_list'
    template_name = 'spexflix/production_list.html'


class ProductionDetail(DetailView):
    model = models.Production
    context_object_name = 'production'
    template_name = 'spexflix/production_detail.html'


class VideoDetail(DetailView):
    model = models.Video
    context_object_name = 'video'
    template_name = 'spexflix/video_detail.html'


class ProductionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Production.objects.all()
    serializer_class = serializers.ProductionSerializer