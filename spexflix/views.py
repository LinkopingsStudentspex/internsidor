from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from rest_framework import viewsets, permissions
from . import models, serializers

@method_decorator(login_required, name='dispatch')
class ProductionList(ListView):
    model = models.Production
    context_object_name = 'production_list'
    template_name = 'spexflix/production_list.html'


@method_decorator(login_required, name='dispatch')
class ProductionDetail(DetailView):
    model = models.Production
    context_object_name = 'production'
    template_name = 'spexflix/production_detail.html'


@method_decorator(login_required, name='dispatch')
class VideoDetail(DetailView):
    model = models.Video
    context_object_name = 'video'
    template_name = 'spexflix/video_detail.html'


class ProductionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Production.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.ProductionSerializer