from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.http import urlencode
from django.views.generic import DetailView, ListView, UpdateView
from django.urls import reverse, reverse_lazy

from . import forms, models

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

@login_required
def view_recipients(request, alias):
    try:
        email_list = models.EmailList.objects.get(alias=alias)
    except models.EmailList.DoesNotExist:
        return HttpResponseNotFound()
    
    return HttpResponse('{}'.format(email_list.get_recipients()))

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
class PersonUpdateView(UpdateView):
    form_class = forms.PersonForm
    template_name = 'batadasen/person_self.html'
    success_url = reverse_lazy('batadasen:person_self')

    def get_object(self, queryset=None):
        return get_object_or_404(models.Person, user=self.request.user)
