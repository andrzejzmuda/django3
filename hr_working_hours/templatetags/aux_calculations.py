from django import template
from hr_working_hours.models import WorkingHours, LastDay, ManagerToWorker, HolidayTypes
import datetime
from django.db.models import Q
from canteen.models import UserCompanyCard
from django.contrib.auth.models import User

register = template.Library()


def daterange(date1, date2):
    for n in range(int((date2 - date1).days)+1):
        yield date1 + datetime.timedelta(n)


@register.filter(name='days_off')
def days_off(user):
    days_off = 0
    try:
        findDaysOff = WorkingHours.objects.filter(Q(shortsign=user),
                                                  Q(entry_time__year=datetime.datetime.now().year),
                                                  Q(accepted=True),
                                                  Q(holiday=True),
                                                  Q(holiday_type__type='UW') | Q(holiday_type__type='NZ'))
    except:
        findDaysOff = 0
    for n in findDaysOff:
        for dt in daterange(n.entry_time, n.leaving_time):
            if dt.weekday() not in {5, 6}:
                days_off += 1
    return days_off


@register.simple_tag
def days_off_month(**kwargs):
    week_start = kwargs['week_start']
    week_end = kwargs['week_end']
    user = kwargs['user']
    days_off_month = 0
    try:
        findDaysOff = WorkingHours.objects.filter(Q(shortsign=user),
                                                  Q(entry_time__range=[
                                                      datetime.datetime.strptime(week_start, '%d-%m-%Y'),
                                                      datetime.datetime.strptime(week_end, '%d-%m-%Y')
                                                                       ]),
                                                  Q(accepted=True),
                                                  Q(holiday=True),
                                                  Q(holiday_type__type='UW') | Q(holiday_type__type='NZ'))
    except:
        findDaysOff = 0
    for n in findDaysOff:
        for dt in daterange(n.entry_time, n.leaving_time):
            if dt.weekday() not in {5, 6}:
                days_off_month += 1
    return days_off_month


@register.filter(name='find_last_day')
def find_last_day(worker):
    try:
        last_day = LastDay.objects.get(worker=worker).last_day
    except:
        last_day = 'not found'
    return last_day


@register.filter(name='find_last_day_id')
def find_last_day_id(worker):
    try:
        last_day_id = LastDay.objects.get(worker=worker).id
    except:
        last_day_id = 'not found'
    return last_day_id


@register.filter(name='find_company')
def find_company(worker):
    try:
        company = UserCompanyCard.objects.get(user__username=worker).company.name
    except:
        company = 'not found'
    return company


@register.filter(name='find_manager')
def find_manager(worker):
    try:
        manager = ManagerToWorker.objects.get(worker__username=worker).manager
    except:
        manager = 'not found'
    return manager


@register.filter(name='find_manager_id')
def find_manager_id(worker):
    try:
       manager = ManagerToWorker.objects.get(worker__username=worker).id
    except:
        manager = 0
    return manager


@register.filter(name='find_manager_username')
def find_manager_username(manager):
    try:
       manager = User.objects.get(id=manager).username
    except:
        manager = 'not found'
    return manager


@register.filter(name='find_holiday_type')
def find_holiday_type(holiday_type):
    try:
        type = HolidayTypes.objects.get(id=holiday_type).type
    except:
        type = ''
    return type
