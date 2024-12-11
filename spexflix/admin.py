from django.contrib import admin
from . import models

class SubtitleTrackInline(admin.TabularInline):
    model = models.SubtitleTrack
    extra = 0

class VideoAdmin(admin.ModelAdmin):
    model = models.Video
    inlines = [SubtitleTrackInline]
    autocomplete_fields = ('production',)
    list_display = ('__str__', 'video_type')

class ProductionAdmin(admin.ModelAdmin):
    model = models.Production
    list_display = ('short_name', 'title', 'year', 'subtitle')
    search_fields = ('short_name', 'title', 'year')


admin.site.register(models.Production, ProductionAdmin)
admin.site.register(models.Video, VideoAdmin)
