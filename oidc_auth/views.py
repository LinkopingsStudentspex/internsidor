from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import generics, filters
from rest_framework_api_key.permissions import HasAPIKey

import django_filters

from batadasen.models import Person
from . import serializers


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

@login_required
def user_count(request):
    user_count = Person.objects.filter(~Q(user=None)).count()
    body = {'count': user_count}
    return JsonResponse(body)
