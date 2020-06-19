# -*- coding: utf-8 -*-
from django.db import models
from core.models import Location
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


class RegisterManager(models.Manager):
    def get_by_natural_key(self, card, timestamp):
        return self.get(card=card, TimeStampIn=timestamp)


class TimeRegister(models.Model):
    card = models.CharField(max_length=255)
    TimeStampIn = models.DateTimeField(null=True, blank=True)
    TimeStampOut = models.DateTimeField(null=True, blank=True)
    uploaded = models.BooleanField(default=False)

    objects = RegisterManager()

    def natural_key(self):
        return self.card, self.TimeStampIn

    class Meta:
        managed = True
        db_table = 'register_timeregister'
        verbose_name_plural = 'Time Register'
        unique_together = [['card', 'TimeStampIn']]
        app_label = 'hr_working_hours'

    def __str__(self):
        return self.card, self.TimeStampIn, self.uploaded


class HolidayTypes(models.Model):
    type = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        app_label = 'hr_working_hours'
        verbose_name_plural = 'Holiday Types'
        permissions = (
            ("view_holiday_types", "Can see Holiday Types"),
        )

    def __str__(self):
        return '%s %s' % (self.type, self.description)


class WorkingHours(models.Model):
    source_id = models.BigIntegerField(null=True, unique=True)
    card = models.CharField(max_length=255)
    shortsign = models.CharField(max_length=255, null=True)
    entry_time = models.DateTimeField(null=True)
    leaving_time = models.DateTimeField(null=True)
    accepted = models.BooleanField(default=False)
    total_time = models.DurationField(null=True, blank=True)
    extra_time = models.DurationField(null=True, blank=True)
    holiday = models.BooleanField(default=False)
    accepted_by = models.CharField(max_length=100, null=True, blank=True)
    holiday_type = models.ForeignKey(HolidayTypes, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = 'hr_working_hours'
        verbose_name_plural = 'Working Hours'
        permissions = (
            ("view_working_hours", "Can see Working Hours"),
            ("can_draw_report", "Can draw a report")
        )

    def __str__(self):
        return '%s %s %s %s' % (self.source_id, self.card, self.entry_time, self.leaving_time)


class LocationToManager(models.Model):
    location = models.ManyToManyField(Location)
    manager = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = 'hr_working_hours'
        verbose_name_plural = 'Locations to Manager'
        permissions = (
            ("view_location_to_manager", "Can see Location to Manager"),
        )

    def get_location(self):
        return "\n".join([l.location for l in self.location.all()])

    def get_detailed_location(self):
        return "\n".join([l.detailed_location for l in self.location.all()])

    def __str__(self):
        return '%s %s' % (self.location, self.manager)


class WorkersToLocation(models.Model):
    location = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL)
    workers = models.ManyToManyField(User)

    class Meta:
        app_label = 'hr_working_hours'
        verbose_name_plural = 'Workers to Location'
        permissions = (
            ("view_workers_to_location", "Can see Workers to Location"),
        )

    def __str__(self):
        return '%s %s' % (self.location, self.workers)


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]


class ManagerToWorker(models.Model):
    manager = models.ForeignKey(User, related_name='manager', null=True, blank=True,
                                on_delete=models.SET(get_sentinel_user))
    worker = models.OneToOneField(User, related_name='worker', null=True, unique=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = 'hr_working_hours'
        verbose_name_plural = 'Manager to Workers'
        permissions = (
            ("view_manager_to_worker", "Can see Manager to Worker"),
        )

    def __str__(self):
        return self.manager, self.worker


class LastDay(models.Model):
    worker = models.OneToOneField(User, null=True, on_delete=models.SET_NULL)
    first_day = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    last_day = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)

    class Meta:
        app_label = 'hr_working_hours'
        verbose_name_plural = 'Last days of work'
        permissions = (
            ("view_last_days", "Can view last days"),
        )

    def __str__(self):
        return '%s %s %s' % (self.worker, self.first_day, self.last_day)
