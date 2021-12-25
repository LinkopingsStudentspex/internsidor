from django.contrib import admin

from showcounter import models

class TheatreAdmin(admin.ModelAdmin):
    model = models.Theatre
    search_fields = ['name', 'city']


class PerformanceAdmin(admin.ModelAdmin):
    model = models.Performance
    search_fields = ['production__year', 'production__short_name', 'production__main_title', 'date', 'theatre__name']
    fields = [
        'production',
        'tag',
        'date',
        'start_time',
        'theatre',
        'notes',
    ]

    autocomplete_fields = ['theatre']


class ParticipationAdmin(admin.ModelAdmin):
    model = models.Participation
    autocomplete_fields = ['person', 'performance']
    search_fields = ['person__first_name', 'person__spex_name', 'person__last_name', 'person__member_number']


admin.site.register(models.Performance, PerformanceAdmin)
admin.site.register(models.Theatre, TheatreAdmin)
admin.site.register(models.Participation, ParticipationAdmin)