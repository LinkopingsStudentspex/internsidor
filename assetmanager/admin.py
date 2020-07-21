from django.contrib import admin
from .models import Asset, Owner, Category, AssetModel, LogEntry

admin.site.register(AssetModel)
admin.site.register(Asset)
admin.site.register(Owner)
admin.site.register(Category)
admin.site.register(LogEntry)