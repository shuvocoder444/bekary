from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/calendar/', views.calendar_view, name='calendar'),
    path('dashboard/profile/', views.profile_view, name='profile'),
    path('dashboard/task/', views.task_view, name='task'),
    path('dashboard/forms/', views.forms_view, name='forms'),
    path('dashboard/tables/', views.tables_view, name='tables'),
    path('dashboard/pages/', views.pages_view, name='pages'),
    path('dashboard/charts/', views.charts_view, name='charts'),
    path('dashboard/ui-elements/', views.ui_elements_view, name='ui_elements'),
    path('login/', views.custom_login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]
