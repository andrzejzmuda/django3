from django import template
from django.contrib.auth.models import User


register = template.Library()


@register.filter(name='disponent_name')
def disponent_name(id):
    name = User.objects.filter(disponent__dispo=id).values_list('username')
    return name
