import os
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from napalm import get_network_driver
from netconfapp.models import Device, Backup

def perform_backup(device_id, user_id):
    # Retrieve the device and user
    device = Device.objects.get(id=device_id)
    user = User.objects.get(id=user_id)
   
    device_instances = {}
    driver = get_network_driver(device.vendor)
    device_connection = driver(
        hostname=device.ip,
        username=device.username,
        password=device.password,
        optional_args={
            "port": device.port if device.port else 22,
            "transport": "ssh" if device.vendor != 'nxos' else 'telnet'
        }
    )

    device_connection.open()
    device_instances[device.vendor] = device_connection.get_config()
    running_config = device_instances[device.vendor]['running']
    device_connection.close()
 
        
    timestamp = timezone.localtime().strftime('%Y%m%d%H%M%S')
    backup_file = f"backup_{device.id}_{timestamp}.txt"
    backup_path = os.path.join(settings.MEDIA_ROOT, 'backups', backup_file)
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)

    if running_config:
        with open(backup_path, 'w') as f:
            f.write(running_config)

        # Determine the schedule time and date
        schedule_time = timezone.localtime().replace(microsecond=0).time()
        schedule_date = timezone.localtime().date()

        # Delete existing backup entries with the same schedule_time and schedule_date
        Backup.objects.filter(
            device=device,
            schedule_time=schedule_time,
            schedule_date=schedule_date
        ).delete()

        # Create or update the Backup entry in the database
        Backup.objects.create(
            user=user,
            device=device,
            schedule_time=schedule_time,
            schedule_date=schedule_date,
            configuration=running_config,
            status='success'
        )
    else:
        schedule_time = timezone.localtime().replace(microsecond=0).time()
        schedule_date = timezone.localtime().date()

        # Delete existing backup entries with the same schedule_time and schedule_date
        Backup.objects.filter(
            device=device,
            schedule_time=schedule_time,
            schedule_date=schedule_date
        ).delete()

        # Create or update the Backup entry in the database with failure status
        Backup.objects.create(
            user=user,
            device=device,
            schedule_time=schedule_time,
            schedule_date=schedule_date,
            configuration='',
            status='failed'
        )
