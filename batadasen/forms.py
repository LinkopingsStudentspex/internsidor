from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class ActivationForm(forms.Form):
    username = forms.CharField(label='Användarnamn', max_length=50)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Användarnamnet finns redan.")

        return cleaned_data