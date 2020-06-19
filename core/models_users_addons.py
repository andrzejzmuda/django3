# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django import template
from core.models import get_sentinel_user

register = template.Library()


class Personal_number(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET(get_sentinel_user))
    pers_number = models.CharField(max_length=150, unique=True, blank=True, null=True)

    def __str__(self):
        return '%s %s' % (self.user, self.pers_number)

    class Meta:
        verbose_name_plural = 'Personal Numbers'
        app_label = 'core'


class Consent(models.Model):
    apps = (
        ('Stolowka', 'Stolowka'), # TODO: 'translate it'
        ('hr_working_hours', 'hr_working_hours'),
    )
    consent = models.TextField()
    app = models.CharField(max_length=255, choices=apps, unique=True)

    class Meta:
        app_label = 'core'

    def __str__(self):
        return '%s' % self.consent
