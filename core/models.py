from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]


# sachnr & tabela brakow
class Dispo(models.Model):
    name = models.CharField(max_length=25)
    ekg = models.CharField(max_length=25, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'dispo'
        app_label = 'core'

    def __str__(self):
        return self.name, self.ekg


class Disponent(models.Model):
    dispo = models.ManyToManyField(Dispo)
    shortsign = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user))

    class Meta:
        verbose_name_plural = 'responsible'
        app_label = 'core'

    def __str__(self):
        return '%s %s' % (self.dispo, self.shortsign)


class Sachnr(models.Model):
    sachnr = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200)
    dispo = models.ForeignKey(Dispo, null=True, on_delete=models.SET(get_sentinel_user))
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Sachnummer'
        permissions = (
            ("view_core", "Can see app"),
            ("can_search_for_sachnr", "Can search for sachnr")
        )
        app_label = 'core'

    def __str__(self):
        return self.sachnr, self.description, (self.dispo.name, self.dispo.ekg)


class Deliverer(models.Model):
    number = models.CharField(max_length=150, blank=False)
    name = models.CharField(max_length=250, blank=False)

    class Meta:
        verbose_name_plural = 'deliverers'
        permissions = (
            ("view_core", "Can see app"),
        )
        app_label = 'core'

    def __str__(self):
        return self.number, self.name


class Supplier(models.Model):
    name = models.CharField(max_length=250, blank=False)

    class Meta:
        verbose_name_plural = 'Suppliers'
        app_label = 'core'

    def __str__(self):
        return '%s' % self.name


class Location(models.Model):
    location = models.CharField(max_length=150)
    detailed_location = models.CharField(max_length=250, null=True)

    class Meta:
        verbose_name_plural = 'core_location'
        app_label = 'core'
        permissions = (
            ("edit_location", "Can edit location"),
        )

    def __str__(self):
        return '%s %s' % (self.location, self.detailed_location)
