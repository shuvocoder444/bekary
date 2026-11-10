from django.contrib import admin
from .models import SiteSetting


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'contact_email', 'contact_phone')
    fieldsets = (
        ('General Info', {
            'fields': ('site_name', 'contact_email', 'contact_phone')
        }),
        ('Branding & Assets', {
            'fields': ('site_logo', 'site_logo_dark', 'site_icon', 'favicon')
        }),
    )
