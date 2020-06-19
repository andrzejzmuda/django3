from django import forms
from django.contrib.auth.models import User
from core.models_users_addons import Personal_number
from canteen.models import Company


#personal_number
class PersonalForm(forms.ModelForm):
    class Meta:
        model = Personal_number
        fields = '__all__'


class CreateUserFormStage1(forms.Form):
    shortsign = forms.CharField(label='shortsign', max_length=50)
    pers_number = forms.CharField(label='personal nr', max_length=255, required=False)
    manager = forms.ModelChoiceField(label='supervisor', queryset=User.objects.filter(groups__name='managers'))
    company = forms.ModelChoiceField(label='company', queryset=Company.objects.all())

    def clean_pers_number(self):
        return self.cleaned_data['pers_number'] or None


class CreateUserFormStage2(forms.Form):
    card_original = forms.CharField(label='main card nr', max_length=250, required=False)

    def clean_card_original(self):
        return self.cleaned_data['card_original'] or None


class CreateUserFormStage3(forms.Form):
    first_day = forms.DateField(label='first day at work', required=False)
    last_day = forms.DateField(label='last day at work', required=False)

    def clean_first_day(self):
        return self.cleaned_data['first_day'] or None

    def clean_last_day(self):
        return self.cleaned_data['last_day'] or None
