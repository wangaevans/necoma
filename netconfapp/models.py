from django.contrib.auth.models import User
from django.db import models
import uuid
import subprocess
from django.db import transaction

class Device(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('offline', 'Offline'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    ip = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    vendor = models.CharField(max_length=100)
    port = models.IntegerField(default=22)
    default_configuration_version = models.ForeignKey(
        'Configuration', on_delete=models.SET_NULL, null=True, blank=True, related_name='default_for_device')
    status = models.CharField(max_length=7, choices=STATUS_CHOICES, default='offline')
    has_issues = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    def get_configurations(self):
        return self.configurations.all().order_by('-timestamp')
    
    def get_id(self):
        return self.id
    
    def check_status(self):
        """Check if the device is active or offline."""
        try:
            response = subprocess.call(
                ['ping', '-c', '1', self.ip],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.status = 'active' if response == 0 else 'offline'
        except Exception:
            self.status = 'offline'
        self.save()

    def check_for_issues(self):
        """Check if the device has issues."""
        self.has_issues = False
        self.save()


class Configuration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(
        Device, related_name='configurations', on_delete=models.CASCADE)
    configuration = models.TextField()
    version_tag = models.CharField(max_length=50)
    timestamp = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Add user field
    diff = models.TextField(blank=True)
    updated_config = models.TextField(blank=True)
    config_file = models.FileField(upload_to='config_files', blank=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.set_as_default()

    def set_as_default(self):
        with transaction.atomic():
            device = self.device
            device.default_configuration_version = self
            device.save()


class Backup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    device = models.ForeignKey('Device', on_delete=models.CASCADE, related_name='backups')
    schedule_time = models.TimeField()
    schedule_date = models.DateField()
    configuration = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('success', 'Successful'), ('failed', 'Failed')])
    class Meta:
        unique_together = ('user', 'device', 'schedule_time', 'schedule_date')
    def __str__(self):
        return f"Backup {self.id} for device {self.device} at {self.schedule_time} on {self.schedule_date}"
    
class Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    success = models.BooleanField(default=False)
    details = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} {'(Success)' if self.success else '(Failure)'} at {self.timestamp}"

# class EmailSettings(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     email_host = models.CharField(max_length=255, blank=True, null=True,default="smtp.gmail.com")
#     email_port = models.IntegerField(blank=True, null=True,default=587)
#     email_host_user = models.CharField(max_length=255, blank=True, null=True)
#     email_host_password = models.CharField(max_length=255, blank=True, null=True)
#     email_use_tls = models.BooleanField(default=True)
#     email_use_ssl = models.BooleanField(default=False)

#     def __str__(self) -> str:
#         return self.email_host_user if self.email_host_user else "No Email User"
    