from django.db import models
from django.contrib.auth.models import User
from core.models import get_sentinel_user, Location


class Responsibles(models.Model):
    location = models.ForeignKey(Location, on_delete=models.SET(get_sentinel_user))
    shortsign = models.ManyToManyField(User)

    class Meta:
        verbose_name_plural = 'core_responsibles'
        app_label = 'core'
        permissions = (
            ("edit_responsibles", "Can edit responsibles"),
        )

    def __str__(self):
        return self.location, self.shortsign
