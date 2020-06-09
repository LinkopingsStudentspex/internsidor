from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as origUserAdmin, GroupAdmin as origGroupAdmin
from django.contrib.auth.models import User, Group
from django.core import mail
from django.db import models
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe   
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.translation import gettext, gettext_lazy as _

from .models import *
from . import urls

class ExtraEmailInline(admin.TabularInline):
    model = ExtraEmail
    extra = 0

class ProductionMembershipInline(admin.TabularInline):
    model = ProductionMembership
    extra = 0

    autocomplete_fields = ['group']

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
        ('user', 'send_activation_link'),
        ('lifetime_member', 'honorary_member'),
        'hundred_club',
        'deceased',
        ('wants_spexinfo', 'wants_blandat', 'wants_trams'),
        'notes'
    )

    list_display = [
        'member_number',
        'full_name',
        'email',
        'get_production_groups'
    ]

    search_fields = [
        'member_number',
        'first_name',
        'last_name',
        'spex_name',
        'email'
    ]

    autocomplete_fields = ['user']

    inlines = [
        ProductionMembershipInline,
        AssociationMembershipInline,
        AssociationActivityInline,
        ExtraEmailInline,
    ]

    def full_name(self, obj):
        return obj
    full_name.short_description = 'Namn'

    def get_production_groups(self, obj):
        group_list = []
        count = 0
        for membership in obj.production_memberships.order_by('-group__production__year'):
            count += 1
            if count < 6:
                group_list.append(membership.short_description())
            else:
                group_list.append('...')
                break
        return ', '.join(group_list)
    get_production_groups.short_description = 'Grupper'

    def get_readonly_fields(self, request, obj=None):
        ret_fields = []
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
                render_to_string(
                    template_name='batadasen/activation_email.txt',
                    context={
                        'first_name': activation.person.first_name,
                        'activation_url': request.build_absolute_uri(reverse('batadasen:activate') + '?token=' + activation.token),
                        'login_url': request.build_absolute_uri(reverse('oidc_authentication_init')),
                        'contact_email': settings.DEFAULT_FROM_EMAIL
                    }
                ),
                settings.DEFAULT_FROM_EMAIL,
                [email]
            )
            messages.info(request, 'Ett mail med en aktiveringslänk har skickats till {}. Länken går ut {}'.format(email, activation.valid_until.strftime('%Y-%m-%d %H:%M:%S')))

class UserAdmin(origUserAdmin):
    fieldsets = (
        (None, {'fields': ('username',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

class UserInLine(admin.TabularInline):
    model = Group.user_set.through
    extra = 0

    autocomplete_fields = ['user']

class GroupAdmin(origGroupAdmin):
    inlines = [UserInLine]

class EmailListAdmin(admin.ModelAdmin):
    fields = (
        'alias',
        'opt_in_members',
        'production_groups',
        'all_groups',
        'productions',
        'active_association_groups',
        'association_groups',
        'opt_out_members',
    )
    filter_horizontal = ('opt_in_members', 'opt_out_members', 'all_groups', 'production_groups', 'productions', 'active_association_groups', 'association_groups')

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

class GenericGroupAdmin(admin.ModelAdmin):
    fields = ('short_name', 'name')

class ProductionGroupAdmin(admin.ModelAdmin):
    model = ProductionGroup

    search_fields = ['group_type__short_name', 'group_type__name', 'production__short_name']

admin.site.register(AssociationActivity)
admin.site.register(AssociationMembership)
admin.site.register(AssociationYear)
admin.site.register(EmailList, EmailListAdmin)
admin.site.register(ExtraEmail)
admin.site.register(AssociationGroupType, GenericGroupAdmin)
admin.site.register(AssociationGroup)
admin.site.register(ProductionGroupType, GenericGroupAdmin)
admin.site.register(Instrument, TitleAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Production)
admin.site.register(ProductionGroup, ProductionGroupAdmin)
admin.site.register(Title, TitleAdmin)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
