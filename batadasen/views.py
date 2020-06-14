from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
from django.views.generic import DetailView, ListView, UpdateView

from rest_framework import generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey
import django_filters

from . import forms, models, serializers

User = get_user_model()

def activation_view(request):
    token = request.GET.get('token')
    activations = models.UserActivation.objects.filter(token=token)

    bad_token = False
    if token is None or not activations.exists():
        bad_token = True
    else:
        if timezone.now() > activations.first().valid_until:
            bad_token = True
    
    if bad_token:
        return HttpResponse("Du har nog följt en gammal länk eller så har den kopierats fel")
    
    person = activations.first().person

    if request.method == 'POST':
        form = forms.ActivationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']

            user = User(username=username)
            user.save()


            if person.user is not None:
                person.user.delete()

            person.user = user
            person.save()

            activations.delete()

            return redirect('batadasen:person_self')

    else:
        form = forms.ActivationForm()

    return render(request, 'batadasen/activate.html', {'form': form, 'person': person})


@method_decorator(login_required, name='dispatch')
class EmailListListView(ListView):
    model = models.EmailList

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email_domain'] = settings.EMAIL_DOMAIN
        return context

@method_decorator(login_required, name='dispatch')
class EmailListDetailView(DetailView):
    model = models.EmailList
    fields = ['recipients']
    slug_field = 'alias'
    slug_url_kwarg = 'alias'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email_domain'] = settings.EMAIL_DOMAIN
        return context


@method_decorator(login_required, name='dispatch')
class PersonDetailView(DetailView):
    model = models.Person


@method_decorator(login_required, name='dispatch')
class PersonSelfView(UpdateView):
    form_class = forms.PersonForm
    template_name = 'batadasen/person_self.html'
    success_url = reverse_lazy('batadasen:person_self')

    def get_object(self, queryset=None):
        return models.Person.objects.filter(user=self.request.user).first()

@method_decorator(login_required, name='dispatch')
class ProductionListView(ListView):
    model = models.Production


@method_decorator(login_required, name='dispatch')
class ProductionDetailView(DetailView):
    model = models.Production

    # This dance is done to order the memberships in each group by title
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        groups = []
        for group in context['object'].groups.all():
            memberships = group.memberships.order_by("-title")
            if not memberships.exists():
                continue
            result_group = dict()
            result_group['group'] = group
            result_group['memberships'] = memberships
            groups.append(result_group)
        context['groups'] = groups
        return context

@login_required
def index_view(request):
    return render(request, 'batadasen/index.html')

# Returns a JSON response with a list of users, for use by a keycloak user storage provider.
class UserList(generics.ListAPIView):
    queryset = models.Person.objects.filter(~Q(user=None))
    serializer_class = serializers.PersonSerializer
    permission_classes = [HasAPIKey]
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.SearchFilter
    ]
    filterset_fields = ['user__username', 'email']
    search_fields = ['user__username', 'email', 'first_name', 'last_name', 'member_number']

# Returns a JSON response with a the number of users, for use by a keycloak user storage provider.
@api_view(['GET'])
@permission_classes([HasAPIKey])
def user_count(request):
    user_count = models.Person.objects.filter(~Q(user=None)).count()
    body = {'count': user_count}
    return Response(body)