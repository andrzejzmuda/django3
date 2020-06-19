# -*- coding: utf-8 -*-
from django.contrib.auth.admin import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models_users_addons import Consent


class Company(models.Model):
    name = models.CharField(max_length=250, unique=True)
    discount = models.CharField(max_length=100, verbose_name='discount')

    def __str__(self):
        return '%s %s' % (self.name, self.discount)

    class Meta:
        verbose_name_plural = 'Companies'


class UserCompanyCard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    card = models.CharField(max_length=250, blank=True, null=True)
    card_original = models.CharField(max_length=250, unique=True, blank=True, null=True)
    temp_card_date = models.DateField(default=None, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)

    def clean_card(self):
        return self.clean_fields('card_original') or None

    def __str__(self):
        return '%s %s %s %s %s' % (self.user, self.card, self.card_original, self.temp_card_date,
                                   self.company)


@receiver(post_save, sender=User)
def create_user_company_card(sender, instance, created, **kwargs):
    if created:
        UserCompanyCard.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_company_card(sender, instance, **kwargs):
    try:
        instance.usercompanycard.save()
    except:
        UserCompanyCard.objects.create(user_id=instance.id)


class Product(models.Model):
    name = models.CharField(max_length=250)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return '%s %s' % (self.name, self.price)

    class Meta:
        permissions = (
            ("draw_report", "can draw report"),
        )


class Menu(models.Model):
    date = models.DateField()
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return '%s' % self.product

    class Meta:
        permissions = (
            ("view_stolowka_menu", "can view menu"),
            ("diner_front", "access to diner front")
            )


class Order(models.Model):
    date = models.DateField()
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    complete = models.BooleanField(default=False)

    def __str__(self):
        return '%s %s %s' % (self.date, self.user, self.complete)


class OrderItems(models.Model):
    order = models.ForeignKey(Order, null=True, on_delete=models.SET_NULL)
    product = models.ForeignKey(Menu, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.IntegerField()
    sold = models.BooleanField(default=True)

    def __str__(self):
        return '%s %s %s %s' % (self.order, self.product_id, self.quantity, self.sold)

    class Meta:
        verbose_name_plural = 'OrderItems'


class OrderConsents(models.Model):
    order = models.ForeignKey(Order, null=True, blank=True, related_name='order', on_delete=models.SET_NULL)
    consent = models.ForeignKey(Consent, null=True, blank=True, on_delete=models.SET_NULL)
    answer = models.BooleanField(default=False)

    def __str__(self):
        return '%s %s' % (self.order, self.consent)

    class Meta:
        verbose_name_plural = 'OrderConsents'
