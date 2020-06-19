from django import forms
from django.forms import ModelForm
from hr_working_hours.models import WorkingHours, LocationToManager, WorkersToLocation, LastDay, HolidayTypes
from django.contrib.auth.models import User
from django.db.models import Q


class WorkingHoursForm(ModelForm):
    class Meta:
        model = WorkingHours
        exclude = ['source_id', 'card', 'total_time', 'accepted_by']

    def __init__(self, *args, **kwargs):
        super(WorkingHoursForm, self).__init__(*args, **kwargs)
        self.fields['holiday_type'].queryset = HolidayTypes.objects.all()


class LocationToManagerForm(ModelForm):
    class Meta:
        model = LocationToManager
        fields = '__all__'


class WorkersToLocationForm(ModelForm):
    class Meta:
        model = WorkersToLocation
        fields = '__all__'


class LastDayForm(ModelForm):
    class Meta:
        model = LastDay
        fields = '__all__'


class ManagerToWorkerForm(forms.Form):
    manager = forms.ModelChoiceField(queryset=User.objects.filter(groups__name__icontains='managers'))


class ManagerToWorkersGroupForm(forms.Form):
    manager = forms.ModelChoiceField(queryset=User.objects.filter(groups__name__icontains='managers'))
    workers = forms.ModelMultipleChoiceField(queryset=User.objects.filter(
        ~Q(usercompanycard__company__name='apprentice')))
