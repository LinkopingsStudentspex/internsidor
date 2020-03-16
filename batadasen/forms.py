from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model

User = get_user_model()

class ActivationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']

    username = forms.CharField(
        label='Användarnamn', 
        validators=[
            RegexValidator('^[A-Za-z0-9_-]+$', 'Får endast innehålla engelska bokstäver (A-Z, a-z), siffror (0-9) och tecknen "-" och "_"'),
        ],
        min_length=2)