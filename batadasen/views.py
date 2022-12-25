from django.conf import settings
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q, F, Value
from django.db.models.functions import Concat
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
from django.views.generic import DetailView, ListView, UpdateView, CreateView

from django_filters.filterset import FilterSet

from rest_framework import generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey
import django_filters

import ajax_select as asel

from . import forms, models, serializers
if settings.PROVISION_GSUITE_ACCOUNTS:
    from . import gsuite

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
    
    activation = activations.first()
    person = activation.person

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

            if settings.PROVISION_GSUITE_ACCOUNTS and activation.provision_gsuite_account:
                gsuite.create_user(person.user.username, person.first_name, person.last_name)

            activations.delete()

            return redirect('batadasen:person_settings')

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
        if context['object'].alias.endswith('gruppledare'):
            context['gruppledare'] = True
        return context


@method_decorator(login_required, name='dispatch')
class PersonDetailView(DetailView):
    model = models.Person

    def get_object(self, queryset=None):
        obj = super(PersonDetailView, self).get_object(queryset)
        if (obj.privacy_setting == models.Person.PrivacySetting.PRIVATE
            and not self.request.user.has_perm('batadasen.view_private_info')
            and not self.request.user == obj.user):
            raise Http404()
        return obj

@method_decorator(login_required, name='dispatch')
class PersonSelfView(UpdateView):
    form_class = forms.PersonForm
    template_name = 'batadasen/person_settings.html'
    success_url = reverse_lazy('batadasen:person_settings')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'object' in context:
            context['extra_emails'] = models.ExtraEmail.objects.filter(person=context['object'])
        return context

    def get_object(self, queryset=None):
        return models.Person.objects.filter(user=self.request.user).first()

@method_decorator(login_required, name='dispatch')
class ExtraEmailView(CreateView):
    form_class = forms.ExtraEmailForm
    template_name = 'batadasen/extraemail_form.html'
    success_url = reverse_lazy('batadasen:person_settings')

    def form_valid(self, form):
        if form.is_valid():
            extra_email = form.save(commit=False)
            extra_email.person = self.request.user.person
            extra_email.save()
        return redirect('batadasen:person_settings')


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

            # Exclude persons with private privacy setting for regular users
            if not self.request.user.has_perm('batadasen.view_private_info'):
                memberships = memberships.exclude(person__privacy_setting=models.Person.PrivacySetting.PRIVATE)

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

class EmailListFilter(FilterSet):
    alias = django_filters.CharFilter(field_name='alias', lookup_expr='icontains')
    class Meta:
        model = models.EmailList
        fields = ['alias']

@login_required
def email_list_filter(request):
    context = {}
    context['filter'] = EmailListFilter(request.GET, queryset=models.EmailList.objects.all())
    context['email_domain'] = settings.EMAIL_DOMAIN
    if request.GET.get('alias')is None:
        context['alias_search'] = ""
    else:
        context['alias_search'] = request.GET.get('alias')

    return render(request, 'batadasen/emaillist_filter.html', context)

class UserFilter(FilterSet):
    user__username = django_filters.CharFilter(field_name='user__username', lookup_expr='iexact')
    email = django_filters.CharFilter(field_name='email', lookup_expr='iexact')
    class Meta:
        model = models.Person
        fields = ['user__username', 'email']

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
    filterset_class = UserFilter
    search_fields = ['user__username', 'email', 'first_name', 'last_name', 'member_number']

# Returns a JSON response with the number of users, for use by a keycloak user storage provider.
@api_view(['GET'])
@permission_classes([HasAPIKey])
def user_count(request):
    user_count = models.Person.objects.filter(~Q(user=None)).count()
    body = {'count': user_count}
    return Response(body)

# This is not pretty... we create a dummy page accessible by an url in order to trick
# the admin site that this is the login page that it should redirect to for non-staff-users.
@login_required
def no_admin_view(request):
    return render(request, 'batadasen/no_admin.html')

admin.site.login = login_required(staff_member_required(admin.site.login, login_url='batadasen:no_admin'))


@method_decorator(login_required, name='dispatch')
class EventView(DetailView):
    model = models.Event
    success_url = reverse_lazy('batadasen:event')


@method_decorator(login_required, name='dispatch')
class EventListView(ListView):
    model = models.Event
    success_url = reverse_lazy('batadasen:event_list')


@method_decorator(login_required, name='dispatch')
class CreateEventView(CreateView):
    form_class = forms.EventForm
    template_name = 'batadasen/event_add.html'
    success_url = reverse_lazy('batadasen:person_settings')

    def form_valid(self, form):
        pass


@asel.register('person')
class PersonLookup(asel.LookupChannel):
    model = models.Person

    def check_auth(self, request):
        if not request.user.is_authenticated:
            raise PermissionDenied

    def get_query(self, q, request):
        return self.model.objects\
                         .annotate(name=Concat(F("first_name"), Value(' '), F("spex_name"), Value(' '), F("last_name")))\
                         .filter(name__icontains=q)

    def format_item_display(self, item):
        return f'<span class="person">{item.name}</span>'
