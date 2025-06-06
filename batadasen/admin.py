from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as origUserAdmin, GroupAdmin as origGroupAdmin
from django.contrib.auth.models import User, Group
from django.core import mail
from django.db import models
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.translation import gettext, gettext_lazy as _

from .models import *
from . import urls

if settings.PROVISION_GSUITE_ACCOUNTS:
    from . import gsuite

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
    provision_gsuite_account = forms.BooleanField(required=False, label='Aktivera Google-konto för användaren.')

    def clean(self):
        cleaned_data = super().clean()
        if self.instance.user is not None and cleaned_data['send_activation_link']:
            self.add_error('send_activation_link', 'Personen har redan en aktiv användare. Be en administratör ta bort användaren först!')

        requested_gsuite_activation = 'provision_gsuite_account' in cleaned_data and cleaned_data['provision_gsuite_account']

        if requested_gsuite_activation and self.instance.user is None and not cleaned_data['send_activation_link']:
            self.add_error('provision_gsuite_account', 'Personen har ingen användare och du har inte klickat i att en ny användare ska skapas.')

        if requested_gsuite_activation and not settings.PROVISION_GSUITE_ACCOUNTS:
            self.add_error('provision_gsuite_account', 'Aktivering av Google-konton är inaktiverat.')

        return cleaned_data

class PersonAdmin(admin.ModelAdmin):
    form = PersonForm

    fields = (
        'member_number',
        ('first_name', 'last_name'),
        'spex_name',
        'email',
        'street_address',
        ('postal_code', 'postal_locality', 'country'),
        'phone_mobile',
        ('phone_home', 'phone_work', 'phone_extra'),
        'address_list_email',
        ('user', 'send_activation_link', 'provision_gsuite_account'),
        ('medal_2', 'medal_4', 'medal_6', 'hundred_club'),
        'deceased',
        ('wants_spexinfo', 'wants_blandat', 'wants_trams'),
        'email_active',
        'notes',
        'privacy_setting',
    )

    list_display = [
        'member_number',
        'full_name',
        'email',
        'user_link',
        'get_production_groups',
    ]

    search_fields = [
        'member_number',
        'first_name',
        'last_name',
        'spex_name',
        'email',
        'user__username',
    ]

    autocomplete_fields = ['user']

    inlines = [
        ProductionMembershipInline,
        AssociationMembershipInline,
        AssociationActivityInline,
        ExtraEmailInline,
    ]

    def full_name(self, obj):
        return obj.full_name

    full_name.short_description = 'Namn'

    def user_link(self, obj):
        if obj.user is not None:
            return format_html("<a href='{url}'>{username}</a>", url=reverse('admin:auth_user_change', args=(obj.user.id,)), username=obj.user.username)
        else:
            return "-"
    user_link.short_description = 'Användare'

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
        if not request.user.is_superuser:
            # If anyone with edit-person permissions could change the connections between users and persons,
            # there is nothing that stops a less privileged user from reassigning a super user to their own person,
            # which could allow them to get a password reset link for the super user to their own email.
            ret_fields.append('user')
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

            activation = UserActivation(person=obj, provision_gsuite_account=form.cleaned_data['provision_gsuite_account'])
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
                '"Spexets internsidor" <{}>'.format(settings.DEFAULT_FROM_EMAIL),
                [email]
            )
            messages.info(request, 'Ett mail med en aktiveringslänk har skickats till {}. Länken går ut {}'.format(email, activation.valid_until.strftime('%Y-%m-%d %H:%M:%S')))
        elif settings.PROVISION_GSUITE_ACCOUNTS and form.cleaned_data['provision_gsuite_account'] and obj.user is not None:
            gsuite.create_user(obj.user.username, obj.first_name, obj.last_name)


class UserAdmin(origUserAdmin):
    top_fields = ('username',)
    if 'mozilla_django_oidc' not in settings.INSTALLED_APPS:
        top_fields = ('username','password')

    fieldsets = (
        (None, {'fields': top_fields}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    list_display = [
        'username',
        'person_name',
        'get_auth_groups',
        'is_staff',
    ]

    search_fields = [
        'username',
        'person__first_name',
        'person__last_name',
        'person__member_number',
    ]

    def person_name(self, obj):
        if obj.person is None:
            return ""
        else:
            return obj.person
    person_name.short_description = 'Person'

    def get_auth_groups(self, obj):
        group_list = []
        count = 0
        for group in obj.groups.all():
            count += 1
            group_list.append(group.name)
        return ', '.join(group_list)
    get_auth_groups.short_description = 'Grupprättigheter'

class UserInLine(admin.TabularInline):
    model = Group.user_set.through
    extra = 0

    autocomplete_fields = ['user']

class GroupAdmin(origGroupAdmin):
    inlines = [UserInLine]

class EmailListAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'alias',
                'forward_to',
                'is_internal',
                'opt_in_members',
                'opt_out_members',
            )
        }),
        ('Val för uppsättningslistor', {
            'fields': (
                'production_groups',
                'all_groups',
                'productions',
            ),
            'classes': ('collapse',)
        }),
        ('Val för föreningslistor', {
            'fields': (
                'active_association_groups',
                'association_groups',
            ),
            'classes': ('collapse',)
        }),
        ('Övriga val', {
            'fields': (
                'all_titles',
            ),
            'classes': ('collapse',)
        })
    )
    filter_horizontal = (
        'opt_in_members',
        'opt_out_members',
        'all_groups',
        'production_groups',
        'productions',
        'active_association_groups',
        'association_groups',
        'all_titles',
    )
    autocomplete_fields = ['forward_to']
    search_fields = ['alias']
    list_display = [
        'alias',
        'is_internal',
        'forward_to',
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['alias']
        else:
            return []

class TitleAdmin(admin.ModelAdmin):
    fields = ('name', 'email_alias')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['name']
        else:
            return []

class GenericGroupAdmin(admin.ModelAdmin):
    fields = ('short_name', 'name')

class ProductionGroupTypeAdmin(admin.ModelAdmin):
    fields = ('short_name', 'name', 'exclude_from_production_email')

class ProductionGroupAdmin(admin.ModelAdmin):
    model = ProductionGroup

    search_fields = ['group_type__short_name', 'group_type__name', 'production__short_name']

class UserActivationAdmin(admin.ModelAdmin):
    model = UserActivation
    autocomplete_fields = ['person']

class AssociationMembershipAdmin(admin.ModelAdmin):
    model = AssociationMembership
    list_display = ['year', 'person', 'membership_type']
    list_filter = ['membership_type', 'year']

admin.site.register(AssociationActivity)
admin.site.register(AssociationMembership, AssociationMembershipAdmin)
admin.site.register(AssociationYear)
admin.site.register(EmailList, EmailListAdmin)
admin.site.register(ExtraEmail)
admin.site.register(AssociationGroupType, GenericGroupAdmin)
admin.site.register(AssociationGroup)
admin.site.register(ProductionGroupType, ProductionGroupTypeAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Production)
admin.site.register(ProductionGroup, ProductionGroupAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(UserActivation, UserActivationAdmin)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
