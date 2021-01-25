# -*- coding: utf-8 -*-
from django import forms

from canteen.models import Product, Order, Menu, OrderItems, UserCompanyCard, Company, OrderConsents


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'


class UserCompanyCardForm(forms.ModelForm):
    class Meta:
        model = UserCompanyCard
        fields = '__all__'


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = '__all__'


class ItemsForm(forms.ModelForm):
    class Meta:
        model = OrderItems
        fields = '__all__'


class SearchForm(forms.Form):
    card_id = forms.CharField(max_length=255)


class MyModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '%s %s' % (obj.name, obj.discount)


class CreateUserForm(forms.Form):
    shortsign = forms.CharField(label='shortsign', max_length=50)
    company = forms.ModelChoiceField(queryset=Company.objects.all())
    card = forms.CharField(label='active card nr', max_length=255, required=False)
    temp_card_date = forms.DateField(label='active card valid until:', required=False)
    card_original = forms.CharField(label='primary card nr', max_length=250, required=False)
    pers_number = forms.CharField(label='personal nr', max_length=255, required=False)
    first_day = forms.DateField(label='first day at work', required=False)
    last_day = forms.DateField(label='last day at work', required=False)

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.fields['company'].queryset = Company.objects.all()

    def clean_card_original(self):
        return self.cleaned_data['card_original'] or None

    def clean_card(self):
        return self.cleaned_data['card'] or None


class ConsentForm(forms.ModelForm):
    class Meta:
        model = OrderConsents
        fields = ('answer',)
