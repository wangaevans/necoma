# Generated by Django 5.0.7 on 2024-08-03 14:50

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('netconfapp', '0010_rename_success_backup_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='backup',
            unique_together={('user', 'device', 'schedule_time', 'schedule_date')},
        ),
    ]
