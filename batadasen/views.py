from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from . import forms, models
from django.contrib.auth import get_user_model
from django.utils import timezone

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
            print('Got response with username {}'.format(username))

            user = User(username=username)
            user.save()


            if person.user is not None:
                person.user.delete()

            person.user = user
            person.save()

            activations.delete()

            return HttpResponseRedirect('/')

    else:
        form = forms.ActivationForm()

    return render(request, 'batadasen/activate.html', {'form': form, 'person': person})

def view_recipients(request, alias):
    try:
        email_list = models.EmailList.objects.get(alias=alias)
    except models.EmailList.DoesNotExist:
        return HttpResponseNotFound()
    
    return HttpResponse('{}'.format(email_list.get_recipients()))

