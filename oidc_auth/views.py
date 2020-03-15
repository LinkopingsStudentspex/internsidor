from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Q
from batadasen.models import Person
from . import serializers
from rest_framework import generics, filters
from rest_framework_api_key.permissions import HasAPIKey
import django_filters

def login(request):
    return render(request, 'oidc_auth/login.html')

class UserList(generics.ListAPIView):
    queryset = Person.objects.filter(~Q(user=None))
    serializer_class = serializers.PersonSerializer
    permission_classes = [HasAPIKey]
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.SearchFilter
    ]
    filterset_fields = ['user__username', 'email']
    search_fields = ['user__username', 'email', 'first_name', 'last_name', 'member_number']

def user_count(request):
    user_count = Person.objects.filter(~Q(user=None)).count()
    body = {'count': user_count}
    return JsonResponse(body)
