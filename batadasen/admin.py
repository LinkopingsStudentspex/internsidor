from django.contrib import admin, messages
from django.core import mail
from django.db import models
from django import forms
from .models import *
from django.conf import settings
from django.utils.html import format_html
from django.urls import reverse

class ExtraEmailInline(admin.TabularInline):
    model = ExtraEmail
    extra = 0

class ProductionMembershipInline(admin.TabularInline):
    model = ProductionMembership
    extra = 0

class AssociationMembershipInline(admin.TabularInline):
    model = AssociationMembership
    extra = 0

class AssociationActivityInline(admin.TabularInline):
    model = AssociationActivity
    extra = 0

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = '__all__'

    send_activation_link = forms.BooleanField(required=False, label='Skicka aktiveringslänk för att skapa ny användare.')

    def clean(self):
        cleaned_data = super().clean()
        if self.instance.user is not None and cleaned_data['send_activation_link']:
            self.add_error('send_activation_link', 'Personen har redan en aktiv användare. Be en administratör ta bort användaren först!')
        return cleaned_data

class PersonAdmin(admin.ModelAdmin):
    form = PersonForm

    fields = (
        'member_number',
        ('first_name', 'last_name', 'maiden_name'),
        'spex_name',
        'email',
        'street_address',
        ('postal_code', 'postal_locality', 'country'),
        'address_list_email',
        'user',
        'send_activation_link',
    )

    inlines = [
        ProductionMembershipInline,
        AssociationMembershipInline,
        AssociationActivityInline,
        ExtraEmailInline,
    ]

    def get_readonly_fields(self, request, obj=None):
        ret_fields = ['user']
        if obj:
            ret_fields.append('member_number')
        
        return ret_fields
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if form.cleaned_data['send_activation_link']:
            email = form.cleaned_data['email']
            if email is None or email == '':
                return
            
            existing_user_activations = UserActivation.objects.filter(person=obj)
            if existing_user_activations.exists():
                print('Deleting existing user activations in progress')
                existing_user_activations.delete()
            
            activation = UserActivation(person=obj)
            activation.save()

            mail.send_mail('Aktiveringslänk för spexets internsidor',
                '''
                Hej {}!
                Välkommen till spexet! Ett konto har skapats åt dig på spexets interna
                hemsidor. Följ länken nedan för att välja ett användarnamn och aktivera ditt
                konto. Länken fungerar endast en gång.
                http://localhost:8000/batadasen/activate?token={}
                '''.format(activation.person.first_name, activation.token),
                settings.DEFAULT_FROM_EMAIL,
                [email]
            )
            messages.info(request, 'Ett mail med en aktiveringslänk har skickats till {}. Länken går ut {}'.format(email, activation.valid_until.strftime('%Y-%m-%d %H:%M:%S')))


class EmailListAdmin(admin.ModelAdmin):
    fields = (
        'alias',
        'opt_in_members',
        'production_groups',
        'all_groups',
        'productions',
        'opt_out_members',
    )
    filter_horizontal = ('opt_in_members', 'opt_out_members', 'all_groups', 'production_groups', 'productions')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['alias']
        else:
            return []

class TitleAdmin(admin.ModelAdmin):
    fields = ('name',)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['name']
        else:
            return []

class GroupAdmin(admin.ModelAdmin):
    fields = ('short_name', 'name')

admin.site.register(AssociationActivity)
admin.site.register(AssociationMembership)
admin.site.register(AssociationYear)
admin.site.register(EmailList, EmailListAdmin)
admin.site.register(ExtraEmail)
admin.site.register(AssociationGroupType, GroupAdmin)
admin.site.register(ProductionGroupType, GroupAdmin)
admin.site.register(Instrument, TitleAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Production)
admin.site.register(ProductionGroup)
admin.site.register(Title, TitleAdmin)
