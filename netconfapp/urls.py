# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('logs/', views.show_configuration_logs, name='show_logs'),
    path('', views.dashboard, name='home'),
    path('vendors/', views.view_devices_by_os, name='vendors'),
    path('configure-devices/', views.configure_multiple_devices, name='configure_devices'),
    path('delete-device/<uuid:pk>/', views.delete_item, name='delete_device'),
    path('connection-settings/<uuid:pk>/', views.modify_device_connection,
         name='modify_device_connection'),
    path('connect-to-device/', views.connect_to_device, name='connect_device'),
    path('configure-device/<uuid:pk>/', views.configure_device, name='configure_device'),
    path('view-configurations/<uuid:pk>/',
         views.view_configurations, name='view_configurations'),
    path('view-configuration/<uuid:device_pk>/<uuid:config_pk>/',
         views.view_single_configuration, name='view_single_configuration'),
    path('rollback-configuration/<uuid:device_pk>/',
         views.rollback_configuration, name='rollback_configuration'),
    path('schedule-backup/<uuid:pk>/', views.schedule_backup_view, name='schedule_backup'),
    path('backups/', views.show_backups, name='backups'),
    path('view-backup/<uuid:pk>/', views.view_backup_configuration, name='view_backup_configuration'),
#     path('profile-settings/', views.settings_view, name='settings'),
]
