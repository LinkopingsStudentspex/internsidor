from django.contrib import admin
from .models import *

class ExtraEmailInline(admin.TabularInline):
    model = ExtraEmail
    extra = 0

class ProductionMembershipInline(admin.TabularInline):
    model = ProductionMembership
    extra = 0

class AssociationMembershipInline(admin.TabularInline):
    model = AssociationMembership
    extra = 0

class PersonAdmin(admin.ModelAdmin):
    fields = (
        'member_number',
        ('first_name', 'last_name', 'maiden_name'),
        'spex_name',
        'email',
        'street_address',
        ('postal_code', 'postal_locality', 'country'),
        'address_list_email',
    )

    inlines = [
        ProductionMembershipInline,
        AssociationMembershipInline,
        ExtraEmailInline,
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['member_number']
        else:
            return []


class EmailListAdmin(admin.ModelAdmin):
    fields = (
        'alias',
        'opt_in_members',
        'opt_out_members',
        'all_groups',
        'production_groups',
        'productions'
    )
    filter_horizontal = ('opt_in_members', 'opt_out_members', 'all_groups', 'production_groups', 'productions')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['alias']
        else:
            return []

class TitleAdmin(admin.ModelAdmin):
    fields = ('name',)

class GroupAdmin(admin.ModelAdmin):
    fields = ('short_name', 'name')

admin.site.register(AssociationActivity)
admin.site.register(AssociationMembership)
admin.site.register(AssociationYear)
admin.site.register(EmailList, EmailListAdmin)
admin.site.register(ExtraEmail)
admin.site.register(Group)
admin.site.register(Instrument)
admin.site.register(Person, PersonAdmin)
admin.site.register(Production)
admin.site.register(ProductionGroup)
admin.site.register(Title, TitleAdmin)
