from django import forms
from django.forms import ModelForm, inlineformset_factory

from .models import (Category,
                    Department,
                    Events,
                    Owner,
                    Device,
                    History)

class DeviceForm(ModelForm):
    class Meta:
        model = Device
        fields = '__all__'

class OwnerForm(ModelForm):
    class Meta:
        model = Owner
        fields = '__all__'


DeviceFormSet = inlineformset_factory(Device, History, extra=1, fields='__all__', can_delete=True)

class SearchForm(forms.Form):
    actions = (
        [("","")] +
        list(Events.objects.all().values_list('action', 'action'))
        )
    categories = (
        [("","")] +
        list(Category.objects.all().values_list('name', 'name'))
    )

    description = forms.CharField(required=False, label='description')
    category = forms.ChoiceField(required=False, label='category', choices=categories)
    hostname = forms.CharField(required=False, label='hostname')
    serial_number = forms.CharField(required=False, label='serial number')
    mac_address = forms.CharField(required=False, label='MAC address')
    event = forms.ChoiceField(required=False, label='event', choices=actions)
    owner = forms.CharField(required=False, label='owner')


class AssignOwnerForm(forms.Form):
    devices = (
        [("","")] +
        list(Device.objects.all().values_list('id', 'hostname'))
    )

    card = forms.CharField(label='card')
    device = forms.ChoiceField(label='device', choices=devices)


class NewCardForm(forms.Form):
    card = forms.CharField(label='scan card here:')
    user = forms.CharField(label="user's shortsign")