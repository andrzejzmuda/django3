from django import template
from canteen.models import UserCompanyCard
from core.models_users_addons import Personal_number
from django.contrib.auth.models import User
register = template.Library()


@register.filter(name='user_name')
def user_name(order__user_id):
    user_name = UserCompanyCard.objects.get(user_id=order__user_id).user.username
    return (user_name)

@register.filter(name='comp_name')
def comp_name(order__user_id):
    comp_name = UserCompanyCard.objects.get(user_id=order__user_id).company
    return (comp_name)


@register.filter(name='first_name')
def first_name(order__user_id):
    first_name = User.objects.get(id=order__user_id).first_name
    return (first_name)


@register.filter(name='last_name')
def last_name(order__user_id):
    last_name = User.objects.get(id=order__user_id).last_name
    return (last_name)


@register.filter(name='find_pers_number')
def pers_number(order__user_id):
    try:
        pers_number = Personal_number.objects.get(user_id=order__user_id).pers_number
    except:
        pers_number = ''
    return (pers_number)
