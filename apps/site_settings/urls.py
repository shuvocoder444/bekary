from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/settings/', views.site_settings_view, name='settings'),
    path('dashboard/site-settings/', views.site_settings_view, name='site_settings'),
]
