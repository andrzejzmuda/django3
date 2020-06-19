from django import template
from canteen.models import UserCompanyCard
from core.models_users_addons import Personal_number

register = template.Library()


@register.filter(name='company')
def company(pk):
    try:
        company = UserCompanyCard.objects.get(user_id=pk).company
    except:
        company = ''
    return company


@register.filter(name='pers_number')
def pers_number(pk):
    try:
        pers_number = Personal_number.objects.get(user_id=pk).pers_number
    except:
        pers_number = ''
    return pers_number

