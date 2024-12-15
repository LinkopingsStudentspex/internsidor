from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
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

def auth_check(request):
    """
    Empty response for use with Nginx auth_request
    """
    if request.user.is_authenticated:
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=401, headers={'WWW-Authenticate': 'Bearer'})

class ProductionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Production.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.ProductionSerializer