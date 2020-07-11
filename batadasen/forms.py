from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

from . import models

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
        min_length=2,
        max_length=150,
        help_text='Tänk på att användarnamnet är skiftlägeskänsligt, "Lisse" är alltså inte samma användarnamn som "lisse".')

    def __init__(self, *args, **kwargs):
        super(ActivationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            'username',
            Submit('submit', 'Aktivera!')
        )

class PersonForm(forms.ModelForm):
    class Meta:
        model = models.Person
        fields = (
            'first_name',
            'spex_name',
            'last_name',
            'street_address',
            'postal_locality',
            'postal_code',
            'country',
            'email',
            'address_list_email',
            'phone_mobile',
            'phone_home',
            'phone_work',
            'phone_extra',
            'wants_spexinfo',
            'wants_blandat',
            'wants_trams',
            'privacy_setting'
        )
    
    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-3 mb-0'),
                Column('spex_name', css_class='form-group col-md-3 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'street_address',
            Row(
                Column('postal_code', css_class='form-group col-md-2 mb-0'),
                Column('postal_locality', css_class='form-group col-md-5 mb-0'),
                Column('country', css_class='form-group col-md-5 mb-0'),
                css_class='form-row'
            ),
            'email',
            'address_list_email',
            'phone_mobile',
            'phone_home',
            'phone_work',
            'wants_spexinfo',
            'wants_blandat',
            'wants_trams',
            'privacy_setting',
            Submit('submit', 'Uppdatera!')
        )

class ExtraEmailForm(forms.ModelForm):
    class Meta:
        model = models.ExtraEmail
        fields = ('email',)