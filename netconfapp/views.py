from uuid import UUID

import pytz
from netconfapp.scheduler import schedule_backup
from netconfapp.utils import send_alert_email
from .forms import BackupScheduleForm,  MultiDevicesConfigurationForm
from datetime import datetime
from django.utils.timezone import make_aware
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from .models import Backup, Configuration, Device,  Log
from .forms import DeviceForm, ConfigurationForm
from napalm import get_network_driver
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Device, Configuration, Log, Backup
from .forms import BackupScheduleForm
from django.db.models import Count

# @login_required
# def settings_view(request):
#     email_settings, created = EmailSettings.objects.get_or_create(
#         user=request.user)

#     if request.method == 'POST':
#         form = EmailSettingsForm(request.POST, instance=email_settings)
#         if form.is_valid():
#             form.save()
#             return redirect('home')
#     else:
#         form = EmailSettingsForm(instance=email_settings)

#     return render(request, 'settings.html', {'form': form})
def view_backup_configuration(request, pk):
    backup = get_object_or_404(Backup, id=pk)
     # Fetch the device associated with the backup
    device = backup.device
    device_id=device.get_id()
    if isinstance(device_id, UUID):
        device_id = str(device_id)
    # Handle rollback functionality
    if request.method == "POST":
        try:
            # Rollback the configuration (implementation may vary)
            device.apply_configuration(backup.configuration)
            messages.success(request, "Configuration rolled back successfully.")
        except Exception as e:
            messages.error(request, f"Failed to rollback configuration: {e}")
        return redirect('backups')
    
    return render(request, 'view_backup_configuration.html', {'backup': backup,'device_id': device_id})

def schedule_backup_view(request, pk):
    device = get_object_or_404(Device, pk=pk)
    if request.method == 'POST':
        form = BackupScheduleForm(request.POST)
        if form.is_valid():
            backup_schedule = form.save(commit=False)
            backup_schedule.device = device
            backup_schedule.save()
            # Schedule the backup job
            if backup_schedule.is_active:
                schedule_backup(backup_schedule, request.user)  # Pass the user to the scheduling function
            
            messages.success(request, f'Backup scheduled successfully for device {device}.')
            return redirect('home')
    else:
        form = BackupScheduleForm(initial={'device': device})
    return render(request, 'schedule_backup.html', {'form': form})

from asgiref.sync import async_to_sync

@login_required
def show_backups(request):
    """
    View to display configuration backups.
    
    :param request: HTTP request object.
    :return: Rendered configuration logs page.
    """
    
    schedules = Backup.objects.order_by('-created_at')
    eat = pytz.timezone('Africa/Nairobi')
    current_datetime = timezone.now().astimezone(eat)
    current_time = current_datetime.time()
    
    context = {
        'schedules': schedules,
        'current_time': current_time,
    }
    return render(request, 'view_backups.html', context)



@login_required
def show_configuration_logs(request):
    """
    View to display configuration logs.

    :param request: HTTP request object.
    :return: Rendered configuration logs page.
    """
    configuration_logs = Log.objects.order_by('-timestamp')
    return render(request, 'configuration_logs.html', {'logs': configuration_logs})


@login_required
def delete_item(request, pk):
    """
    View to delete a device.

    :param request: HTTP request object.
    :param pk: Primary key of the device to delete.
    :return: Redirect to home page or rendered error page.
    """
    item = get_object_or_404(Device, pk=pk)
    if request.method == 'POST':
        try:
            item.delete()
            subject = f'Delete : {item.username}'
            message = f'The device with IP {item.ip} has been deleted from the inventory.'
            # Add your recipients here
            recipient_list = ['wangaevans84@gmail.com']
            send_alert_email(subject, message, recipient_list)
            Log.objects.create(
                user=request.user, action=f'Delete device {item.username}', success=True)
            return redirect('/')
        except Exception as e:
            Log.objects.create(
                user=request.user, action=f'Delete device {item.username}', success=False, details=str(e))


@login_required
def dashboard(request):
    """
    View to display the dashboard.

    :param request: HTTP request object.
    :return: Rendered dashboard page.
    """
    devices = Device.objects.all()

    # Update the status and issue flags for each device
    for device in devices:
        device.check_status()
        device.check_for_issues()
        if device.status == 'offline':
            subject = f'Device Offline: {device.username}'
            message = f'The device with IP {device.ip} is currently offline.'
            recipient_list = ['wangaevans84@gmail.com']
            try:
                send_alert_email(subject, message, recipient_list)
            except Exception as e:
                pass

    total_devices = devices.count()
    active_devices = devices.filter(status='active').count()
    offline_devices = devices.filter(status='offline').count()
    devices_with_issues = devices.filter(has_issues=True).count()

    # Data for the chart
    config_counts = Configuration.objects.values('device__username').annotate(
        count=Count('id')).order_by('device__username')
    device_names = [item['device__username'] for item in config_counts]
    config_data = [item['count'] for item in config_counts]

    context = {
        'devices': devices,
        'total_devices': total_devices,
        'active_devices': active_devices,
        'offline_devices': offline_devices,
        'devices_with_issues': devices_with_issues,
        'device_names': device_names,
        'config_data': config_data,
    }
    return render(request, 'dashboard.html', context)


@login_required
def rollback_configuration(request, device_pk):
    """
    View to rollback a device's configuration.

    :param request: HTTP request object.
    :param device_pk: Primary key of the device to rollback.
    :return: Redirect to home page or rendered error page.
    """
    device = get_object_or_404(Device, pk=device_pk)
    versions = Configuration.objects.filter(
        device=device).order_by('-timestamp')
    if request.method == 'POST':
        config_pk = request.POST.get('config_pk')
        if config_pk:
            device = get_object_or_404(Device, pk=device_pk)
            configuration = get_object_or_404(Configuration, pk=config_pk)

            try:
                driver = get_network_driver(device.vendor)
                with driver(hostname=device.ip, username=device.username, password=device.password, optional_args={"port": device.port if device.port else 22, "transport": "ssh" if device.vendor != 'nxos' else 'telnet'}) as device_connection:
                    device_connection.open()
                    device_connection.load_merge_candidate(
                        config=configuration.updated_config)
                    device_connection.commit_config()
                    device_connection.close()

                device.default_configuration_version = configuration
                device.save()

                messages.success(request, f'Rolled back to {configuration.version_tag} successfully.')
                Log.objects.create(user=request.user, action=f'Roll back to {configuration.version_tag} on {device.username}', success=True)
                subject = f'Roll back to: {configuration.version_tag} on {device.username} successful'
                message = f'Rollback to:{configuration.version_tag} on device with IP {device.ip} successful.'
                recipient_list = ['wangaevans84@gmail.com']
                try:
                    send_alert_email(subject, message, recipient_list)
                except Exception as e:
                    pass

                return redirect('/')
            except Exception as e:
                error_message = str(e)
                subject = f'Rollback Failed: {device.username}'
                message = f'Rollback to device with IP {device.ip} failed with error message {error_message}.'
                recipient_list = ['wangaevans84@gmail.com']
                try:
                    send_alert_email(subject, message, recipient_list)
                except Exception as e:
                    pass
                Log.objects.create(user=request.user, action=f'Roll back to {configuration.version_tag} on {device.username}', success=False, details=error_message)
                return render(request, 'error.html', {'error_message': error_message})
        else:
            # messages.error(request, 'Please select a version to rollback to.')
            return redirect('rollback_configuration', device_pk=device_pk)
    return render(request, 'rollback_configuration.html', {'device': device, 'versions': versions})


@login_required
def view_configurations(request, pk):
    """
    View to display configurations of a device.

    :param request: HTTP request object.
    :param pk: Primary key of the device.
    :return: Rendered configurations page.
    """
    device = get_object_or_404(Device, pk=pk)
    configurations = device.get_configurations()
    return render(request, 'configurations.html', {'device': device, 'configurations': configurations})


@login_required
def view_devices_by_os(request):
    """
    View to display devices categorized by their operating systems.

    :param request: HTTP request object.
    :return: Rendered devices by OS page.
    """
    all_devices = Device.objects.all()
    cisco = all_devices.filter(vendor__in=['nxos', 'ios', 'iosxr'])
    aristas = all_devices.filter(vendor='eos')
    juniper = all_devices.filter(vendor='junos')
    return render(request, 'devices_by_vendors.html', {'cisco': cisco, 'aristas': aristas, 'juniper': juniper})


@login_required
def view_single_configuration(request, device_pk, config_pk):
    """
    View to display a single configuration of a device.

    :param request: HTTP request object.
    :param device_pk: Primary key of the device.
    :param config_pk: Primary key of the configuration.
    :return: Rendered single configuration page.
    """
    device = get_object_or_404(Device, pk=device_pk)
    configuration = get_object_or_404(device.configurations, pk=config_pk)
    return render(request, 'single_configuration.html', {'device': device, 'configuration': configuration})


@login_required
def modify_device_connection(request, pk):
    """
    View to modify a device's connection details.

    :param request: HTTP request object.
    :param pk: Primary key of the device.
    :return: Redirect to home page or rendered modify device connection page.
    """
    device = get_object_or_404(Device, pk=pk)

    if request.method == 'POST':
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            if form.instance.ip == device.ip and \
               form.instance.username == device.username and \
               form.instance.password == device.password and \
               form.instance.vendor == device.vendor and \
               form.instance.port == device.port:
                Log.objects.create(
                    user=request.user, action=f'Modify connection details for device {device.username}', success=True)
                form.save()
            else:
                Log.objects.create(
                    user=request.user, action=f'Modify connection details for device {device.username}', success=False)
            return redirect('/')
    else:
        form = DeviceForm(instance=device)

    return render(request, 'modify_device_connection.html', {'form': form})


@login_required
def configure_device(request, pk):
    """
    View to configure a device.

    :param request: HTTP request object.
    :param pk: Primary key of the device.
    :return: Redirect to home page or rendered configure device page.
    """
    device = get_object_or_404(Device, pk=pk)
    if request.method == 'POST':
        form = ConfigurationForm(request.POST)
        if form.is_valid():
            configuration = form.cleaned_data['commands']
            user = request.user
            try:
                driver = get_network_driver(device.vendor)
                with driver(hostname=device.ip, username=device.username, password=device.password,
                            optional_args={"port": device.port or 22,
                                           "transport": "ssh" if device.vendor != 'nxos' else 'telnet'}) as device_connection:
                    device_connection.open()
                    device_connection.load_merge_candidate(
                        config=configuration)
                    diff = device_connection.compare_config()
                    if len(diff) > 0:
                        device_connection.commit_config()
                        updated_config = device_connection.get_config(
                            retrieve='running', sanitized=True)['running']
                        device_connection.close()
                        timestamp = make_aware(datetime.now())
                        new_version_tag = f"v{device.configurations.count() + 1}"
                        device.configurations.create(
                            configuration=configuration,
                            version_tag=new_version_tag,
                            user=user,
                            timestamp=timestamp,
                            diff=diff,
                            updated_config=updated_config
                        )
                        messages.success(
                            request, 'Configuration applied successfully.')
                        Log.objects.create(user=request.user, action=f'Configure {device.username}', success=True, details=f'A new configuration version ({new_version_tag}) has been applied successfully.')
                    else:
                        device_connection.discard_config()
                        messages.success(request, 'No changes made.')
                        Log.objects.create(user=request.user, action=f'Configure {device.username}', success=False, details="No configuration changes made on this device")
                    return redirect('/')
            except Exception as e:
                error_message = str(e)
                return render(request, 'error.html', {'error_message': error_message})
    else:
        form = ConfigurationForm()
    return render(request, 'configure_device.html', {'form': form, 'device': device})


@login_required
def configure_multiple_devices(request):
    """
    View to configure multiple devices.

    :param request: HTTP request object.
    :return: Redirect to home page or rendered configure multiple devices page.
    """
    if request.method == 'POST':
        form = MultiDevicesConfigurationForm(request.POST, request.FILES)
        if form.is_valid():
            selected_devices = form.cleaned_data["devices"]
            command_or_file = form.cleaned_data['command_or_file']
            configuration = form.cleaned_data['commands']
            config_file = form.cleaned_data['config_file']
            user = request.user

            try:
                for device in selected_devices:
                    driver = get_network_driver(device.vendor)
                    with driver(hostname=device.ip, username=device.username, password=device.password,
                                optional_args={"port": device.port or 22,
                                               "transport": "ssh" if device.vendor != 'nxos' else 'telnet'}) as device_connection:
                        device_connection.open()
                        if command_or_file == 'command':
                            device_connection.load_merge_candidate(
                                config=configuration)
                        elif command_or_file == 'file':
                            device_connection.load_merge_candidate(
                                filename=config_file.temporary_file_path())
                        diff = device_connection.compare_config()
                        if len(diff) > 0:
                            device_connection.commit_config()
                            updated_config = device_connection.get_config(
                                retrieve='running', sanitized=True)['running']
                            timestamp = make_aware(datetime.now())
                            new_version_tag = f"v{device.configurations.count() + 1}"
                            device.configurations.create(
                                configuration=configuration,
                                version_tag=new_version_tag,
                                user=user,
                                timestamp=timestamp,
                                diff=diff,
                                updated_config=updated_config
                            )
                            Log.objects.create(user=request.user, action=f'Configure multiple devices',
                                               success=True, details=f'Configuration applied successfully to {device.username}')
                        else:
                            device_connection.discard_config()
                            Log.objects.create(user=request.user, action=f'Configure multiple devices',
                                               success=False, details=f"No configuration changes made on {device.username}")
                messages.success(
                    request, 'Configuration applied successfully.')
                return redirect('/')
            except Exception as e:
                error_message = str(e)
                return render(request, 'error.html', {'error_message': error_message})
    else:
        form = MultiDevicesConfigurationForm()
    return render(request, 'configure_multidevices.html', {'form': form})


@login_required
def connect_to_device(request):
    if request.method == 'POST':
        ip = request.POST.get('ip')
        username = request.POST.get('username')
        password = request.POST.get('password')
        vendor = request.POST.get('vendor')
        port = request.POST.get('port', '22')

        device, created = Device.objects.get_or_create(
            username=username,
            defaults={'ip': ip, 'password': password,
                      'vendor': vendor, 'port': port}
        )
        try:
            # device_instances = {}

            driver = get_network_driver(vendor)
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
            # device_instances[vendor] = device_connection.get_config()
            # startup_config = device_instances[vendor]['startup']
            device_connection.close()
            # device_connection.load_merge_candidate(
            #                     config=startup_config)
            # diff = device_connection.compare_config()
            
            # if len(diff)>0:
            #     device.startup_config = startup_config
            #     new_version_tag = f"v{device.configurations.count() + 1}"
            #     timestamp = make_aware(datetime.now())
                # device.configurations.create(
                #     version_tag=new_version_tag,
                #     user=request.user,
                #     timestamp=timestamp,
                #     updated_config=startup_config
                # )

            device.save()
            Log.objects.create(
                user=request.user, action=f'Create device {device.username}', success=True)

            return redirect('/')

        except Exception as e:
            error_message = str(e)
            Log.objects.create(
                user=request.user, action=f'Create device {device.username}', success=False, details={'error': error_message})
            return render(request, 'error.html', {'error_message': error_message})

    else:
        return render(request, 'connect_to_device.html')
