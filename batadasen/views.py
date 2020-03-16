from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.http import urlencode
from django.views.generic import DetailView
from django.urls import reverse

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

@login_required
def person_self_view(request):
    try:
        person = models.Person.objects.get(user=request.user)
    except models.Person.DoesNotExist:
        return HttpResponseNotFound()
    
    return render(request, 'batadasen/person_self.html', {'person': person, 'logout_url': settings.LOGOUT_REDIRECT_URL + '?' + urlencode({'redirect_uri': request.build_absolute_uri(reverse('oidc_authentication_init'))})})
