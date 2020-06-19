from django import forms
from core.models import Sachnr, Disponent, Dispo


#Sachnr and Tabela Brakow
class SachnrForm(forms.ModelForm):
    class Meta:
        model = Sachnr
        fields = '__all__'


class DisponentForm(forms.ModelForm):
    class Meta:
        model = Disponent
        fields = '__all__'
        dispo = forms.ModelChoiceField(queryset=Dispo.objects.all())
        user = forms.ModelChoiceField(queryset=Disponent.objects.all())


class UploadFileForm(forms.Form):
    file = forms.FileField()


class DispoForm(forms.ModelForm):
    class Meta:
        model = Dispo
        fields = '__all__'
