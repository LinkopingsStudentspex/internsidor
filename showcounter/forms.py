from django import forms
from django.forms import widgets
from django.utils.safestring import mark_safe
import batadasen
import showcounter

class PerformanceForm(forms.Form):
    number = forms.IntegerField(required=False, widget=widgets.HiddenInput)
    date = forms.DateField(disabled=True, required=False)
    tag = forms.CharField(disabled=True, required=False)
    theatre = forms.CharField(disabled=True, required=False)
    participated = forms.BooleanField(required=False)
