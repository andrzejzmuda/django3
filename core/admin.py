from django.contrib import admin
from core.models import Sachnr, Dispo, Disponent, Deliverer, Supplier
from core.models_managers_locations import Location, Responsibles
from core.models_users_addons import Personal_number, Consent

# Register your models here.
admin.site.register(Dispo)
admin.site.register(Disponent)
admin.site.register(Location)
admin.site.register(Responsibles)


@admin.register(Sachnr)
class SachnrAdmin(admin.ModelAdmin):
    search_fields = ['sachnr', 'description', 'dispo__name']


@admin.register(Deliverer)
class DelivererAdmin(admin.ModelAdmin):
    search_fields = ['number', 'name']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Personal_number)
class PersonalNumberAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'pers_number']


@admin.register(Consent)
class ConsentsAdmin(admin.ModelAdmin):
    search_fields = ['consent']

