from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache


class SiteSetting(models.Model):
    site_name = models.CharField(max_length=255, default="Dashboard")
    site_logo = models.FileField(upload_to="site_logo/", blank=True, null=True, help_text="Light mode logo (.png, .jpg, .svg)")
    site_logo_dark = models.FileField(upload_to="site_logo/", blank=True, null=True, help_text="Dark mode logo (.png, .jpg, .svg)")
    site_icon = models.FileField(upload_to="site_logo/", blank=True, null=True, help_text="Collapsed sidebar icon (.png, .jpg, .svg)")
    favicon = models.FileField(upload_to="site_logo/", blank=True, null=True, help_text="Favicon (.ico, .png, .svg)")
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_name


@receiver(post_save, sender=SiteSetting)
def clear_site_settings_cache(sender, instance, **kwargs):
    cache.delete('global_site_setting')
