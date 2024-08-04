from .models import Backup
from django import forms
from .models import Device


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['ip', 'username', 'password', 'vendor', 'port']


class ConfigurationForm(forms.Form):
    command_or_file = forms.ChoiceField(
        choices=[('command', 'Type in Commands'),
                 ('file', 'Upload a configuration file')],
        label="Select an option"
    )
    commands = forms.CharField(
        widget=forms.Textarea, required=False, label="Commands")
    config_file = forms.FileField(required=False, label="")


class MultiDevicesConfigurationForm(forms.Form):
    devices = forms.ModelMultipleChoiceField(
        queryset=Device.objects.all(),
        # widget=HorizontalCheckboxSelectMultiple,
        widget=forms.CheckboxSelectMultiple(),
        label="Devices"
    )
    command_or_file = forms.ChoiceField(
        choices=[('command', 'Type in Commands'),
                 ('file', 'Upload a configuration file')],
        label="Select an option"
    )
    commands = forms.CharField(
        widget=forms.Textarea, required=True, label="Commands")
    config_file = forms.FileField(required=True, label="")


class RollbackForm(forms.Form):
    version = forms.ChoiceField(label='Select the Version to Rollback to')

    def __init__(self, versions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['version'].choices = versions


class BackupScheduleForm(forms.ModelForm):
    class Meta:
        model = Backup
        fields = ['device','schedule_time', 'schedule_date']
        widgets = {
            'schedule_date': forms.DateInput(attrs={'type': 'date'}),
            'schedule_time': forms.TimeInput(attrs={'type': 'time'}),
        }


# class EmailSettingsForm(forms.ModelForm):
#     class Meta:
#         model = EmailSettings
#         fields = [
#                   'email_host',
#                   'email_port',
#                   'email_host_user',
#                   'email_host_password',
#                   'email_use_tls',
#                   'email_use_ssl']