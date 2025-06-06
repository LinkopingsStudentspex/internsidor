from datetime import datetime

from django.conf import settings
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.utils.http import urlencode
from django.views.generic import DetailView, ListView, UpdateView, CreateView, TemplateView
from django_filters.filterset import FilterSet
import django_tables2 as tables

from rest_framework import generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey
import django_filters

from . import forms, models, serializers
from showcounter.models import Performance

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


class PersonTable(tables.Table):
    member_number = tables.URLColumn(verbose_name="Medlem")
    spex_name = tables.Column(default="")

    class Meta:
        model = models.Person
        template_name = "django_tables2/bootstrap4-responsive.html"
        fields = ("member_number", "first_name", "last_name", "spex_name")
        row_attrs = {
            "class": lambda record: "text-muted font-italic" if record.deceased else ""
        }


@method_decorator(login_required, name='dispatch')
class PersonListView(tables.SingleTableView):
    table_class = PersonTable
    queryset = models.Person.objects.filter(member_number__lt=5000).all()
    template_name = "person_list.html"
    table_pagination = False



@method_decorator(login_required, name='dispatch')
class PersonDetailView(DetailView):
    model = models.Person


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

            if not memberships.exists():
                continue
            result_group = dict()
            result_group['group'] = group
            result_group['memberships'] = memberships
            groups.append(result_group)
        context['groups'] = groups

        previous_production = (
            self.model.objects.filter(number__lt=context["object"].number)
            .order_by("-number")
            .only("number")
            .first()
        )
        context["previous"] = previous_production.number if previous_production else None

        next_production = (
            self.model.objects.filter(number__gt=context["object"].number)
            .only()
            .order_by("number")
            .only("number")
            .first()
        )
        context["next"] = next_production.number if next_production else None

        return context
    

method_decorator(login_required, name='dispatch')
class AssociationYearListView(ListView):
    model = models.AssociationYear


@method_decorator(login_required, name='dispatch')
class AssociationYearDetailView(DetailView):
    model = models.AssociationYear

    # This dance is done to order the activities in each group by title
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        groups = []
        for group in context['object'].groups.all():
            activities = group.activities.order_by("-title")
            if not activities.exists():
                continue
            result_group = {
                'group': group,
                'activities': activities,
            }
            groups.append(result_group)
        context['groups'] = groups
        
        previous_year = (
            self.model.objects.filter(end_year__lt=context["object"].end_year)
            .order_by("-end_year")
            .only("end_year")
            .first()
        )
        context["previous"] = previous_year.end_year if previous_year else None
        next_year = (
            self.model.objects.filter(end_year__gt=context["object"].end_year)
            .only()
            .order_by("end_year")
            .only("end_year")
            .first()
        )
        context["next"] = next_year.end_year if next_year else None
        return context


@method_decorator(login_required, name='dispatch')
class Club100(ListView):
    model = models.Person
    annotated = model.objects.annotate(
        performances_count=Count('performances')
    )
    queryset = annotated.filter(Q(hundred_club=True) | Q(performances_count__gte=90))
    template_name = 'batadasen/hundraklubben_list.html'

@method_decorator(login_required, name='dispatch')
class Medals(TemplateView):
    template_name = 'batadasen/medals_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['medal_2'] = []
        context['medal_2_candidates'] = []
        context['medal_4'] = []
        context['medal_4_candidates'] = []
        context['medal_6'] = []
        context['medal_6_candidates'] = []
        for person in models.Person.objects.all():
            if person.medal_6:
                context['medal_6'].append(person)
            elif person.currently_active and len(person.active_years) >= 6:
                context['medal_6_candidates'].append(person)

            if person.medal_4:
                context['medal_4'].append(person)
            elif person.currently_active and len(person.active_years) >= 4:
                context['medal_4_candidates'].append(person)

            if person.medal_2:
                context['medal_2'].append(person)
            elif person.currently_active and len(person.active_years) >= 2:
                context['medal_2_candidates'].append(person)
        return context


@method_decorator(login_required, name='dispatch')
class StatisticsView(TemplateView):
    template_name = 'batadasen/statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = datetime.now()
        current_association_year = now.year + (now.month > 6)
        print(now)
        context['years_since_start'] = now.year - 1980 + (now > datetime(now.year, 11, 28))

        honorary = (
            models.AssociationMembership.objects
            .filter(membership_type='HON', person__deceased=False)
            .values_list('person', flat=True)
        )
        
        lifetime = (
            models.AssociationMembership.objects
            .filter(membership_type='LIF', person__deceased=False)
            .exclude(person__in=honorary)
            .values_list('person', flat=True)
        )

        standard = (
            models.AssociationMembership.objects
            .filter(year=current_association_year, membership_type='STD', person__deceased=False)
            .exclude(person__in=honorary)
            .exclude(person__in=lifetime)
            .values_list('person', flat=True)
        )

        honorary = len(honorary)
        lifetime = len(lifetime)
        standard = len(standard)

        context['members'] = {
            'standard': standard,
            'lifetime': lifetime,
            'honorary': honorary,
            'all': standard + lifetime + honorary,
            'ever': models.Person.objects.count()
        }

        not_really_productions = {
            32,  # Jubel-25: fest
            33,  # Jubel-25: prylar
            42,  # Gyckel
            55,  # Jubel-40
            57,  # Covid
        }

        regular_productions = models.Production.objects.filter(regular=True).exclude(number__in=not_really_productions).count()
        extra_productions = models.Production.objects.filter(regular=False).exclude(number__in=not_really_productions).count()
        context['productions'] = {
            'regular': regular_productions,
            'extra': extra_productions,
            'all': regular_productions + extra_productions
        }

        context["performances"] = Performance.objects.filter(date__lte=now).count()

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
