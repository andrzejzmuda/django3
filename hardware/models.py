from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from datetime import datetime


def deleted_user():
    get_user_model().objects.get_or_create(username='deleted')[0]

def user_folder(instance, filename):
    if instance.owner:
        return 'hardware/{0}/{1}'.format(instance.owner.kzz.username, filename)
    else:
        return 'hardware/{0}/{1}'.format('IT', filename)

def managers_only():
        return {'groups__name': 'managers'}

def set_mac_address(instance):
    if len(instance) == 12 and ":" not in instance:
        address = ':'.join(instance[i:i+2] for i in range(0,len(instance),2))
    else:
        address = instance
    return '{0}'.format(address)


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        app_label = "hardware"


class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        app_label = "hardware"


class Events(models.Model):
    action = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.action

    class Meta:
        verbose_name_plural = "Events"
        app_label = "hardware"


class Owner(models.Model):
    kzz = models.ForeignKey(User, related_name='kzz', blank=True, on_delete=models.SET(deleted_user))
    department = models.ForeignKey(Department, blank=True, null=True, on_delete=models.SET_NULL)
    supervisor = models.ForeignKey(
        User, related_name='supervisor', blank=True, null=True,
        on_delete=models.SET(deleted_user), limit_choices_to=managers_only
        )

    def __str__(self):
        return self.kzz.username

    class Meta:
        app_label = "hardware"


class Device(models.Model):
    """
    Contains basic data of a device.
    Draws category data from :model:`hardware.History`
    """
    description = models.CharField(max_length=255, blank=False)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    hostname = models.CharField(max_length=255, blank=True, unique=True)
    serial_number = models.CharField(max_length=255, blank=True)
    mac_address = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        if self.mac_address:
            self.mac_address = set_mac_address(self.mac_address)
        super().save(*args, **kwargs)

    def __str__(self):
        return '%s %s %s %s' % (self.description, self.category, self.hostname,
        self.serial_number)

    class Meta:
        app_label = "hardware"
        unique_together = ['hostname', 'description']


class History(models.Model):
    """
    Describes current state of a device, draws data from :model:`hardware.Device`,
    :model:`hardware.Event` and :model:`hardware.Owner`.
    """
    device = models.ForeignKey(Device, null=True, on_delete=models.SET_NULL)
    assigned = models.DateField(auto_now_add=True, blank=True, null=True)
    decomissioned = models.DateField(auto_now=True, blank=True, null=True)
    event = models.ForeignKey(Events, null=True, on_delete=models.SET_NULL)
    uploaded = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    attachment = models.FileField(upload_to=user_folder, blank=True, null=True)
    owner = models.ForeignKey(Owner, max_length=255, null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        if self.attachment:
            self.uploaded = datetime.utcnow()
        super().save(*args, **kwargs)

    def __str__(self):
        return '%s %s %s %s' % (self.device, self.assigned, self.event, self.owner)

    class Meta:
        app_label = "hardware"
        verbose_name_plural = "History"
