from django.contrib import admin
from .models import Profile, Asset, Price

@admin.register(Profile)
class ProfileAmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth']
    raw_id_fields = ['user']

admin.site.register(Asset)
admin.site.register(Price)
