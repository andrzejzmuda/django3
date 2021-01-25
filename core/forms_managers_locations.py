from django import forms

from core.models_managers_locations import Location, Responsibles


#managers and locations
class ResponsibleForm(forms.ModelForm):
    class Meta:
        model = Responsibles
        fields = '__all__'
        location = forms.ModelChoiceField(queryset=Location.objects.all())
        responsible = forms.ModelChoiceField(queryset=Responsibles.objects.all())


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = '__all__'
