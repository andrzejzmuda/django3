from django.forms import ModelForm

from instructions.models import Instructions


class InstructionsForm(ModelForm):
    class Meta:
        model = Instructions
        fields = '__all__'
