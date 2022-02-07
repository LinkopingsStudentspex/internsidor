from typing import Text
from django.db.models import Count, Q, IntegerField, BooleanField, ExpressionWrapper
from django.db import transaction
from django.http.response import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.forms import formset_factory, TextInput

from batadasen.models import Production
from showcounter.forms import PerformanceForm
from showcounter.models import Performance, Participation

def overview(request):
    user = request.user
    if not user.person:
        return 'Current user is not connected to a person'
    
    productions = Production.objects.annotate(
        num_participations=Count(
            'performances',
            filter=Q(performances__participants__person=user.person)
        )).order_by('-number')
    total_participations = Participation.objects.filter(person=user.person).count()

    context = {
        'productions': productions,
        'total_participations': total_participations
    }
    return render(request, 'showcounter/overview.html', context)

def production(request, number):
    user = request.user
    if not user.person:
        return 'Current user is not connected to a person'

    with transaction.atomic():
        production = get_object_or_404(Production, number=number)
        PerformanceFormSet = formset_factory(
            extra=0, 
            form=PerformanceForm
        )
        context = {
            'production': production,
        }

        if request.method == 'POST':
            performance_formset = PerformanceFormSet(request.POST)
            if not performance_formset.is_valid():
                context['performance_formset'] = performance_formset
                return render(request, 'showcounter/production.html', context)
    
            for form in performance_formset:
                number = form.cleaned_data['number']
                if form.cleaned_data['participated']:
                    try:
                        performance = Performance.objects.get(number=number)
                    except Performance.DoesNotExist:
                        return HttpResponseBadRequest()
                    Participation.objects.get_or_create(performance=performance, person=user.person)
                else:
                    Participation.objects.filter(performance__number=number, person=user.person).delete()
            return redirect('showcounter:overview')

        performances = Performance.objects.filter(production=production).order_by('date')
        initial = []
        for performance in performances:
            current_user_participated = performance.participants.filter(person__member_number=user.person.member_number).exists()
            initial.append({
                'number': performance.number,
                'tag': performance.tag,
                'date': performance.date,
                'theatre': performance.theatre.name,
                'participated': current_user_participated,
            })
    
        context['performance_formset'] = PerformanceFormSet(initial=initial)
        return render(request, 'showcounter/production.html', context)
