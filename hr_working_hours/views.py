# -*- coding: utf-8 -*-
from django.template import loader
from django.shortcuts import reverse, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User, Group
from django.forms.models import modelformset_factory
import datetime
from django.utils import timezone
import os
import json
import csv
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django3_apps.settings import BASE_DIR
from django.conf import settings
import glob
import time
import pytz

from hr_working_hours.models import WorkingHours, LocationToManager, WorkersToLocation, LastDay, ManagerToWorker,\
    HolidayTypes
from core.models import Location
from .forms import WorkingHoursForm, LocationToManagerForm, WorkersToLocationForm, LastDayForm,\
    ManagerToWorkersGroupForm, ManagerToWorkerForm
from canteen.models import UserCompanyCard, Company
from django.db.models import Q, ExpressionWrapper, Sum, DurationField, F, TimeField, DecimalField

from calendar import monthrange


local_tz = pytz.timezone('Europe/Warsaw')

@permission_required('hr_working_hours.view_working_hours')
def main(request):
    template = loader.get_template('main.html')
    return HttpResponse(template.render({}, request))


@permission_required('hr_working_hours.view_location_to_manager')
def LocToMan(request):
    template = loader.get_template('loc_to_man.html')
    try:
        find_managers = Group.objects.get(name='managers').id
    except:
        find_managers = Group.objects.create(name='managers').id
    users = User.objects.filter(groups=find_managers)
    loc_to_man = LocationToManager.objects.all()
    locations = Location.objects.all()
    diff = []
    for all in users:
        found = False
        for sub in loc_to_man:
            if sub.manager_id == all.id:
                found = True
                break
        if not found:
            diff.append(all)
    if request.method == 'POST':
        form = LocationToManagerForm(request.POST)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse('hr_working_hours:LocToMan'))
    else:
        form = LocationToManagerForm()
    context = {'form': form, 'users': diff, 'locations': locations,
               'all': loc_to_man
               }
    return HttpResponse(template.render(context, request))


@permission_required('hr_working_hours.view_location_to_manager')
def loc_to_man_delete(request, pk):
    delete = get_object_or_404(LocationToManager, pk=pk).delete()
    if request.method == 'POST':
        form = LocationToManagerForm(request.POST, instance=delete)
        form.u.delete()
        form.save()
    return HttpResponseRedirect(reverse('hr_working_hours:LocToMan'))


@permission_required('hr_working_hours.change_workinghours')
def loc_to_man_edit(request, pk):
    template = loader.get_template('loc_to_man_edit.html')
    edit = LocationToManager.objects.get(pk=pk)
    manager_selected = User.objects.filter(locationtomanager__id=pk)
    managers = User.objects.filter(groups__name__icontains='managers')
    loc_to_man = LocationToManager.objects.all()
    locations_all = Location.objects.all()
    diff = []
    for all in managers:
        found = False
        for sub in loc_to_man:
            if sub.manager_id == all.id:
                found = True
                break
        if not found:
            diff.append(all)
    EditFormSet = modelformset_factory(LocationToManager, fields=('location',), max_num=1, min_num=0)
    if request.method == 'POST':
        formset = EditFormSet(request.POST, queryset=LocationToManager.objects.filter(pk=pk))
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(reverse('hr_working_hours:LocToMan'))
    else:
        formset = EditFormSet(queryset=LocationToManager.objects.filter(pk=pk))
    context = {'id': pk, 'form': formset, 'edit': edit, 'manager_selected': manager_selected,
               'locations_all': locations_all, 'managers': diff}
    return HttpResponse(template.render(context, request))


@permission_required('hr_working_hours.change_workinghours')
def WorkerToLoc(request):
    template = loader.get_template('worker_to_loc.html')
    user_company = UserCompanyCard.objects.filter(~Q(company__name__icontains='apprentice'))
    try:
        my_locations = LocationToManager.objects.filter(manager_id=request.user.id)\
            .values('location__location', 'location__detailed_location', 'location__id')
    except:
        my_locations = LocationToManager.objects.all()
    context = {'my_locations': my_locations, 'user_company': user_company}
    return HttpResponse(template.render(context, request))


@permission_required('hr_working_hours.change_workerstolocation')
def worker_to_loc_edit(request):
    template = loader.get_template('worker_to_loc_edit.html')
    users = User.objects.filter(
        ~Q(usercompanycard__company__name__icontains='apprentice'),
        ~Q(username__icontains='deleted')
    )
    loc_to_worker = WorkersToLocation.objects.all()
    locations = Location.objects.all()
    locations_diff = []
    workers_diff = []
    for all in locations:
        found = False
        for sub in loc_to_worker:
            if sub.location_id == all.id:
                found = True
                break
        if not found:
            locations_diff.append(all)
    for all in users:
        found = False
        for sub in loc_to_worker.values('workers__id'):
            if sub['workers__id'] == all.id:
                found = True
                break
        if not found:
            workers_diff.append(all)
    if request.method == 'POST':
        form = WorkersToLocationForm(request.POST)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse('hr_working_hours:worker_to_loc_edit'))
    else:
        form = WorkersToLocationForm()
    context = {'form': form, 'locations_diff': locations_diff, 'users': users, 'locations': locations,
               'loc_to_worker': loc_to_worker, 'workers_diff': workers_diff}
    return HttpResponse(template.render(context, request))


@permission_required('hr_working_hours.change_workerstolocation')
def worker_to_loc_edit_single(request, pk):
    template = loader.get_template('worker_to_loc_edit_single.html')
    edit = WorkersToLocation.objects.get(id=pk)
    form = WorkersToLocationForm(request.POST, instance=edit)
    users = User.objects.filter(~Q(usercompanycard__company__name__icontains='apprentice'), ~Q(username='deleted'))
    locations = Location.objects.all()
    loc_to_worker = WorkersToLocation.objects.all()
    locations_diff = []
    workers_diff = []
    for all in locations:
        found = False
        for sub in loc_to_worker:
            if sub.location_id == all.id:
                found = True
                break
        if not found:
            locations_diff.append(all)
    for all in users:
        found = False
        for sub in loc_to_worker.values('workers__id'):
            if sub['workers__id'] == all.id:
                found = True
                break
        if not found:
            workers_diff.append(all)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('hr_working_hours:worker_to_loc_edit'))
    else:
        form = WorkersToLocationForm(instance=edit)
        form.fields['workers'].queryset = User.objects.filter(
            ~Q(usercompanycard__company__name__icontains='praktykanci'),
            ~Q(username='deleted'))
    context = {'edit': edit, 'form': form, 'locations_diff': locations_diff, 'workers_diff': workers_diff}
    return HttpResponse(template.render(context, request))


@permission_required('hr_working_hours.delete_workerstolocation')
def worker_to_loc_edit_single_delete(request, pk):
    previous_page = request.META.get('HTTP_REFERER')
    item = WorkersToLocation.objects.get(pk=pk).delete()
    if request.method == 'POST':
        form = WorkersToLocationForm(request.POST, instance=item)
        form.u.delete()
        form.save()
    return HttpResponseRedirect(reverse('hr_working_hours:worker_to_loc_edit'))



@permission_required('hr_working_hours.change_workerstolocation')
def my_workers_in_loc(request, location):
    template = loader.get_template('my_workers_in_loc.html')
    today = datetime.date.today()
    current_start_month = datetime.date(today.year, today.month, 1)
    current_end_month = today.replace(day=monthrange(today.year, today.month)[1])
    if today.month == 1:
        minus_one_start_month = datetime.date(today.year-1, today.month-1 or 12, 1)
    else:
        minus_one_start_month = datetime.date(today.year, today.month-1 or 12, 1)
    if minus_one_start_month.month == 1:
        minus_two_start_month = datetime.date(minus_one_start_month.year-1, minus_one_start_month.month-1 or 12, 1)
    else:
        minus_two_start_month = datetime.date(minus_one_start_month.year, minus_one_start_month.month-1 or 12, 1)
    if minus_two_start_month.month == 1:
        minus_three_start_month = datetime.date(minus_two_start_month.year-1, minus_two_start_month.month-1 or 12, 1)
    else:
        minus_three_start_month = datetime.date(minus_two_start_month.year, minus_two_start_month.month-1 or 12, 1)
    if minus_three_start_month.month == 1:
        minus_four_start_month = datetime.date(minus_three_start_month.year-1, minus_three_start_month.month-1 or 12, 1)
    else:
        minus_four_start_month = datetime.date(minus_three_start_month.year, minus_three_start_month.month-1 or 12, 1)
    minus_one_end_month = minus_one_start_month.replace(day=monthrange(minus_one_start_month.year,
                                                                       minus_one_start_month.month)[1])
    minus_two_end_month = minus_two_start_month.replace(day=monthrange(minus_two_start_month.year,
                                                                       minus_two_start_month.month)[1])
    minus_three_end_month = minus_three_start_month.replace(day=monthrange(minus_three_start_month.year,
                                                                           minus_three_start_month.month)[1])
    minus_four_end_month = minus_four_start_month.replace(day=monthrange(minus_four_start_month.year,
                                                                         minus_four_start_month.month)[1])
    current_start_week = today - datetime.timedelta(today.weekday() + 1)
    current_end_week = current_start_week + datetime.timedelta(6)
    minus_one_start_week = today + datetime.timedelta(days=-today.weekday(), weeks=-1, hours=-3)
    minus_one_end_week = minus_one_start_week + datetime.timedelta(6)
    minus_two_start_week = today + datetime.timedelta(days=-today.weekday(), weeks=-2, hours=-3)
    minus_two_end_week = minus_two_start_week + datetime.timedelta(6)
    minus_three_start_week = today + datetime.timedelta(days=-today.weekday(), weeks=-3, hours=-3)
    minus_three_end_week = minus_three_start_week + datetime.timedelta(6)
    minus_four_start_week = today + datetime.timedelta(days=-today.weekday(), weeks=-4, hours=-3)
    minus_four_end_week = minus_four_start_week + datetime.timedelta(6)
    selected_location = Location.objects.get(id=location)
    my_workers = WorkersToLocation.objects.filter(Q(location=selected_location.id), Q(workers__is_active=True),
                                                  ~Q(workers__usercompanycard__company__name='apprentice'))\
        .distinct().values('workers__username', 'workers__worker__manager__username',
                           'workers__usercompanycard__company__name', 'workers__id')\
        .order_by('workers__worker__manager__username')
    context = {'selected_location': selected_location, 'my_workers': my_workers,
               'current_start_month': current_start_month, 'current_end_month': current_end_month,
               'minus_one_start_month': minus_one_start_month, 'minus_one_end_month': minus_one_end_month,
               'minus_two_start_month': minus_two_start_month, 'minus_two_end_month': minus_two_end_month,
               'minus_three_start_month': minus_three_start_month, 'minus_three_end_month': minus_three_end_month,
               'minus_four_start_month': minus_four_start_month, 'minus_four_end_month': minus_four_end_month,
               'current_start_week': current_start_week, 'current_end_week': current_end_week,
               'minus_one_start_week': minus_one_start_week, 'minus_one_end_week': minus_one_end_week,
               'minus_two_start_week': minus_two_start_week, 'minus_two_end_week': minus_two_end_week,
               'minus_three_start_week': minus_three_start_week, 'minus_three_end_week': minus_three_end_week,
               'minus_four_start_week': minus_four_start_week, 'minus_four_end_week': minus_four_end_week}
    return HttpResponse(template.render(context, request))


@permission_required('hr_working_hours.change_workinghours')
def my_workers_in_loc_edit(request, worker, week_start, week_end, location):
    template = loader.get_template('my_workers_in_loc_edit.html')
    previous_page = request.META.get('HTTP_REFERER')
    selected_start_week = request.get_full_path().rsplit('/', 2)[1]
    selected_end_week = request.get_full_path().rsplit('/', 1)[1]
    entry_times = [datetime.time(5, 50),
                   datetime.time(13, 50),
                   datetime.time(21, 50)]
    leaving_times = [datetime.time(13, 50),
                     datetime.time(21, 50),
                     datetime.time(5, 50)]
    my_workers = WorkersToLocation.objects.filter(Q(location=location), Q(workers__is_active=True),
                                                  ~Q(workers__usercompanycard__company__name='apprentice'))\
        .distinct().values('workers__username', 'workers__worker__manager__username')\
        .order_by('workers__worker__manager__username')
    start = datetime.datetime.combine(
        datetime.datetime.strptime(week_start, "%d-%m-%Y"), datetime.time(0, 0)) + datetime.timedelta(hours=-1)
    end = datetime.datetime.combine(
        datetime.datetime.strptime(week_end, "%d-%m-%Y"), datetime.time(23, 59))
    today = datetime.datetime.today()
    current_start_week = today - datetime.timedelta(today.weekday() + 1)
    current_end_week = current_start_week + datetime.timedelta(6)
    plus_one_start_week = today + datetime.timedelta(days=-(today.weekday() + 1), weeks=+1, hours=-3)
    plus_one_end_week = plus_one_start_week + datetime.timedelta(6)
    plus_two_start_week = today + datetime.timedelta(days=-(today.weekday() + 1), weeks=+2, hours=-3)
    plus_two_end_week = plus_two_start_week + datetime.timedelta(6)
    minus_one_start_week = today + datetime.timedelta(days=-(today.weekday() + 1), weeks=-1, hours=-3)
    minus_one_end_week = minus_one_start_week + datetime.timedelta(6)
    minus_two_start_week = today + datetime.timedelta(days=-(today.weekday() + 1), weeks=-2, hours=-3)
    minus_two_end_week = minus_two_start_week + datetime.timedelta(6)
    zone = timezone.now()
    workdays = []
    reports = []
    get_worker_id = User.objects.get(username=worker).id
    delta = end.date() - start.date()
    working_time = WorkingHours.objects.filter(Q(shortsign=worker), (
            (Q(entry_time__range=[start, end])) | Q(leaving_time__range=[start, end]))).values().order_by('entry_time')
    # working_hours_sum = working_time.filter(Q(holiday=False)).aggregate(
    #     basic_hours=ExpressionWrapper(Sum(F('total_time') / 60), output_field=TimeField()))['basic_hours']
    # over_hours_sum = working_time.filter(Q(holiday=False)).aggregate(
    #     over_hours=ExpressionWrapper(Sum(F('extra_time') / 60), output_field=TimeField()))['over_hours'] #TODO: in exchange to script.js
    days_off_list = WorkingHours.objects.filter(Q(shortsign=worker), Q(entry_time__year=datetime.datetime.now().year),
                                                Q(holiday=True))
    days_off = WorkingHours.objects.filter(Q(shortsign=worker), Q(entry_time__year=datetime.datetime.now().year),
                                           Q(holiday=True), Q(accepted=True),
                                           (Q(holiday_type__type='UW')
                                            | Q(holiday_type__type='NZ'))
                                           ).aggregate(days=ExpressionWrapper(Sum(F('total_time')),
                                                                              output_field=DurationField()))['days']
    days_off_current_month = WorkingHours.objects.filter(Q(shortsign=worker), Q(entry_time__month=start.month),
                                                         Q(holiday=True), Q(accepted=True), (Q(holiday_type__type='UW')
        | Q(holiday_type__type='NZ'))).aggregate(days=ExpressionWrapper(Sum(F('total_time')),
                                                                        output_field=DurationField()))['days']
    for i in range(delta.days + 1):
        day = start.date() + datetime.timedelta(days=i)
        workdays.append(day)
    for all in workdays:
        found = False
        for sub in working_time:
            if sub['entry_time'].date() == all:
                found = True
                reports.append(sub)
        if not found:
            reports.append(all)
    context = {'working_time': working_time, 'zone': zone, 'my_workers': my_workers, 'days_off_list': days_off_list,
               'selected_start_week': selected_start_week, 'selected_end_week': selected_end_week,
               'current_start_week': current_start_week, 'current_end_week': current_end_week,
               'minus_one_start_week': minus_one_start_week, 'minus_one_end_week': minus_one_end_week,
               'minus_two_start_week': minus_two_start_week, 'minus_two_end_week': minus_two_end_week,
               'plus_one_start_week': plus_one_start_week, 'plus_one_end_week': plus_one_end_week,
               'plus_two_start_week': plus_two_start_week, 'plus_two_end_week': plus_two_end_week,
               'week_start': week_start, 'week_end': week_end, 'start': start, 'end': end,
               'previous_page': previous_page, 'location': location, 'days_off': days_off, 'worker': worker,
               'reports': reports, 'get_worker_id': get_worker_id,
               'days_off_current_month': days_off_current_month, 'entry_times': entry_times,
               'leaving_times': leaving_times}
    return HttpResponse(template.render(context, request))


@permission_required('hr_working_hours.change_workinghours')
def my_workers_in_loc_edit_single(request, pk):
    template = loader.get_template('my_workers_in_loc_edit_single.html')
    edit = WorkingHours.objects.get(id=pk)
    next = request.POST.get('next', '/')
    previous_page = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        form = WorkingHoursForm(request.POST, instance=edit)
        if form.is_valid():
            if not form.cleaned_data['holiday']:
                edit.holiday_type = None
            form.save()
            if LocationToManager.objects.filter(manager=request.user.id):
                edit.accepted_by = request.user.username
                edit.save()
            return HttpResponseRedirect(next)
    else:
        form = WorkingHoursForm(instance=edit)
    time_diff_inline(request, edit.id)
    context = {'edit': edit, 'form': form, 'date': edit.entry_time, 'next': next, 'previous_page': previous_page}
    return HttpResponse(template.render(context, request))


@permission_required('hr_working_hours.add_workinghours')
def my_workers_in_loc_create_single(request, worker):
    template = loader.get_template('my_workers_in_loc_create_single.html')
    next = request.POST.get('next', '/')
    previous_page = request.META.get('HTTP_REFERER')
    user = User.objects.get(username=worker).id
    if LastDay.objects.filter(worker_id=user):
        last_day = LastDay.objects.get(worker_id=user).last_day
    else:
        today = datetime.date.today()
        last_day = datetime.date(today.year+1, today.month, today.day)
    if request.method == 'POST':
        form = WorkingHoursForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['accepted'] and LocationToManager.objects.filter(manager=request.user.id):
                form.cleaned_data['accepted_by'] = request.user.username
            form.save()
            return HttpResponseRedirect(next)
    else:
        form = WorkingHoursForm()
    context = {'form': form, 'previous_page': previous_page, 'next': next, 'worker': worker, 'last_day': last_day}
    return HttpResponse(template.render(context, request))


@permission_required('hr_working_hours.add_workinghours')
def my_workers_in_loc_create_single_inline(request, worker, day_selected):
    template = loader.get_template('my_workers_in_loc_create_single.html')
    next = request.POST.get('next', '/')
    previous_page = request.META.get('HTTP_REFERER')
    user = User.objects.get(username=worker).id
    day_selected = datetime.datetime.strptime(day_selected, "%d-%m-%Y")
    if LastDay.objects.filter(worker_id=user):
        last_day = LastDay.objects.get(worker_id=user).last_day
    else:
        today = datetime.date.today()
        last_day = datetime.date(today.year+1, today.month, today.day)
    if request.method == 'POST':
        form = WorkingHoursForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['accepted'] and LocationToManager.objects.filter(manager=request.user.id):
                form.cleaned_data['accepted_by'] = request.user.username
            form.save()
            return HttpResponseRedirect(next)
    else:
        form = WorkingHoursForm()
    context = {'form': form, 'previous_page': previous_page, 'next': next, 'worker': worker, 'last_day': last_day,
               'day_selected': day_selected}
    return HttpResponse(template.render(context, request))


@permission_required('hr_working_hours.change_workinghours')
def my_workers_in_loc_edit_delete(request, pk):
    previous_page = request.META.get('HTTP_REFERER')
    item = WorkingHours.objects.get(id=pk).delete()
    if request.method == 'POST':
        form = WorkingHoursForm(request.POST, instance=item)
        form.u.delete()
        form.save()
    return HttpResponseRedirect(previous_page)


@permission_required('hr_working_hours.can_draw_report')
def hr_reports(request):
    template = loader.get_template('hr_reports.html')
    companies = Company.objects.filter(~Q(name='apprentice')).values('name')
    workers = User.objects.filter(~Q(usercompanycard__company__name='apprentice'), ~Q(username='deleted'))
    context = {'companies': companies, 'workers': workers}
    return HttpResponse(template.render(context, request))


@permission_required('hr_working_hours.can_draw_report')
def hr_report_per_company_modal(request):
    template = loader.get_template('hr_report_per_company_modal.html')
    return HttpResponse(template.render({}, request))


@permission_required('hr_working_hours.can_draw_report')
def hr_report_per_location_modal(request):
    template = loader.get_template('hr_report_per_location_modal.html')
    return HttpResponse(template.render({}, request))


@permission_required('hr_working_hours.can_draw_report')
def hr_report_per_manager_modal(request):
    template = loader.get_template('hr_report_per_manager_modal.html')
    return HttpResponse(template.render({}, request))


@permission_required('hr_working_hours.can_draw_report')
def hr_report_per_user_modal(request):
    template = loader.get_template('hr_report_per_user_modal.html')
    return HttpResponse(template.render({}, request))


@permission_required('hr_working_hours.can_draw_report')
def hr_report_edit_worker_modal(request):
    template = loader.get_template('hr_report_edit_worker_modal.html')
    return HttpResponse(template.render({}, request))


@permission_required('hr_working_hours.can_draw_report') # TODO: revise if it's working correctly!
def hr_report_per_company(request, company, week_start, week_end):
    template = loader.get_template('hr_report_per_company.html')
    start = datetime.datetime.combine(datetime.datetime.strptime(week_start, "%d-%m-%Y"), datetime.time(0, 0))
    end = datetime.datetime.combine(datetime.datetime.strptime(week_end, "%d-%m-%Y"), datetime.time(23, 59))
    employees = User.objects.filter(usercompanycard__company__id=company)
    comp_name = Company.objects.get(id=company)
    columns = ('id', 'source_id', 'card', 'kzz', 'entry_time', 'leaving_time', 'accepted', 'total_time', 'extra_time',
               'holiday', 'accepted_by', 'holiday_type'
               )
    workdays = []
    reports = []
    delta = end.date() - start.date()
    for i in range(delta.days+1):
        day = start.date()+datetime.timedelta(days=i)
        workdays.append(day)
    for n in employees:
        report = WorkingHours.objects.filter(Q(shortsign=n), Q(entry_time__range=[start, end])).values_list().order_by('entry_time')
        for x in report:
            reports.append(dict(zip(columns, x)))
    context = {'reports': reports, 'company': comp_name.name, 'week_start': week_start, 'week_end': week_end}
    return HttpResponse(template.render(context, request))


@permission_required('hr_working_hours.can_draw_report')
def hr_report_per_location(request, location, week_start, week_end):
    template = loader.get_template('hr_report_per_location.html')
    start = datetime.datetime.combine(datetime.datetime.strptime(week_start, "%d-%m-%Y"), datetime.time(0, 0))
    end = datetime.datetime.combine(datetime.datetime.strptime(week_end, "%d-%m-%Y"), datetime.time(23, 59))
    employees = User.objects.filter(Q(workerstolocation__location_id=location))
    location_name = Location.objects.get(id=location)
    columns = ('id', 'source_id', 'card', 'kzz', 'entry_time', 'leaving_time', 'accepted', 'total_time', 'extra_time',
               'holiday', 'accepted_by', 'holiday_type'
               )
    no_entries_columns = ('username', 'last_day', 'manager')
    workdays = []
    no_entries = []
    reports = []
    delta = end.date() - start.date()
    for i in range(delta.days+1):
        day = start.date()+datetime.timedelta(days=i)
        workdays.append(day)
    for n in employees:
        report = WorkingHours.objects.filter(Q(shortsign=n), Q(entry_time__range=[start, end])).values_list()\
            .order_by('entry_time')
        if report:
            for x in report:
                reports.append(dict(zip(columns, x)))
        else:
            if User.objects.filter(Q(username=n), (Q(lastday__last_day__gte=end) | Q(lastday__last_day__isnull=True)),
                                   Q(is_active=True)):
                ommited_user = User.objects.filter(id=n.id).values_list('username', 'lastday__last_day',
                                                                        'worker__manager__username')
                for d in ommited_user:
                    no_entries.append(dict(zip(no_entries_columns, d)))
    context = {'reports': reports, 'location_name': location_name, 'week_start': week_start, 'week_end': week_end,
               'no_entries': no_entries}
    return HttpResponse(template.render(context, request))


@permission_required('hr_working_hours.can_draw_report')
def hr_report_per_manager(request, manager, week_start, week_end):
    template = loader.get_template('hr_report_per_manager.html')
    start = datetime.datetime.combine(datetime.datetime.strptime(week_start, "%d-%m-%Y"), datetime.time(0, 0))
    end = datetime.datetime.combine(datetime.datetime.strptime(week_end, "%d-%m-%Y"), datetime.time(23, 59))
    employees = User.objects.filter(worker__manager=manager)
    columns = ('id', 'source_id', 'card', 'shortsign', 'entry_time', 'leaving_time', 'accepted', 'total_time',
               'extra_time', 'holiday', 'accepted_by', 'holiday_type')
    no_entries_columns = ('username', 'last_day', 'manager')
    workdays = []
    no_entries = []
    reports = []
    delta = end.date() - start.date()
    for i in range(delta.days+1):
        day = start.date()+datetime.timedelta(days=i)
        workdays.append(day)
    for n in employees:
        report = WorkingHours.objects.filter(Q(shortsign=n), Q(entry_time__range=[start, end])).values_list().order_by('entry_time')
        if report:
            for x in report:
                reports.append(dict(zip(columns, x)))
        else:
            if User.objects.filter(Q(username=n), (Q(lastday__last_day__gte=end) | Q(lastday__last_day__isnull=True)),
                                   Q(is_active=True)):
                ommited_user = User.objects.filter(id=n.id).values_list('username', 'lastday__last_day',
                                                                        'worker__manager__username')
                for d in ommited_user:
                    no_entries.append(dict(zip(no_entries_columns, d)))
    context = {'reports': reports, 'week_start': week_start, 'week_end': week_end, 'no_entries': no_entries,
               'manager': manager}
    return HttpResponse(template.render(context, request))


@permission_required('hr_working_hours.can_draw_report')
def hr_report_per_user(request, worker, week_start, week_end):
    template = loader.get_template('hr_report_per_user.html')
    start = datetime.datetime.combine(datetime.datetime.strptime(week_start, "%d-%m-%Y"), datetime.time(0, 0))
    end = datetime.datetime.combine(datetime.datetime.strptime(week_end, "%d-%m-%Y"), datetime.time(23, 59))
    worker = User.objects.get(pk=worker)
    report = WorkingHours.objects.filter(Q(shortsign=worker.username), Q(entry_time__range=[start, end]))\
        .order_by('entry_time')
    workdays = []
    reports = []
    delta = end.date() - start.date()
    for i in range(delta.days+1):
        day = start.date()+datetime.timedelta(days=i)
        workdays.append(day)
    for all in workdays:
        found = False
        for sub in report:
            if sub.entry_time.date() == all:
                found = True
                reports.append(sub)
        if not found:
            reports.append(all)
    context = {'week_start': week_start, 'week_end': week_end, 'worker': worker, 'start': start, 'end': end,
               'reports': reports}
    return HttpResponse(template.render(context, request))


@permission_required('hr_working_hours.change_workinghours')
def hr_accept_entries(request, user, week_start, week_end):
    previous_page = request.META.get('HTTP_REFERER')
    start = datetime.datetime.combine(datetime.datetime.strptime(week_start, "%d-%m-%Y"), datetime.time(0, 0))
    end = datetime.datetime.combine(datetime.datetime.strptime(week_end, "%d-%m-%Y"), datetime.time(23, 59))
    working_time = WorkingHours.objects.filter(Q(shortsign=user), Q(entry_time__range=[start, end]),
                                               Q(leaving_time__isnull=False), Q(accepted=False))
    for n in working_time:
        n.accepted_by = request.user.username
        n.accepted = True
        n.save()
    return HttpResponseRedirect(previous_page)


def daterange(date1, date2):
    for n in range(int((date2 - date1).days)+1):
        yield date1 + datetime.timedelta(n)


@permission_required('hr_working_hours.change_workinghours')
def time_diff_inline(request, pk):
    previous_page = request.META.get('HTTP_REFERER')
    one = WorkingHours.objects.get(pk=pk)
    find_bhp = HolidayTypes.objects.get(type='BHP')
    totalHolidays = datetime.timedelta(days=0)
    if not one.holiday:
        if one.leaving_time and one.entry_time:
            if (one.leaving_time - one.entry_time) > datetime.timedelta(hours=8):
                one.total_time = datetime.timedelta(hours=8)
                one.extra_time = datetime.timedelta(0, (((((one.leaving_time - one.entry_time)
                                                           - datetime.timedelta(hours=8)).seconds/60)/30)*30)*60)
                if one.extra_time > datetime.timedelta(hours=4):
                    one.extra_time = datetime.timedelta(hours=4)
                one.save()
            else:
                one.total_time = one.leaving_time - one.entry_time
                one.extra_time = datetime.timedelta(0, 0)
                one.save()
    if one.holiday and one.leaving_time and one.entry_time and one.holiday_type_id != find_bhp.id:
        if one.leaving_time.date() == one.entry_time.date():
            one.total_time = datetime.timedelta(days=1)
            one.extra_time = datetime.timedelta(0, 0)
            one.save()
        else:
            for dt in daterange(one.entry_time.astimezone(local_tz), one.leaving_time.astimezone(local_tz)):
                if dt.weekday() not in {5, 6}:
                    totalHolidays += datetime.timedelta(days=1)
            one.total_time = totalHolidays
            one.extra_time = datetime.timedelta(0, 0)
            one.save()
    if one.holiday and one.leaving_time and one.entry_time and one.holiday_type_id == find_bhp.id:
        if one.leaving_time.date() == one.entry_time.date():
            one.total_time = datetime.timedelta(hours=8)
            one.extra_time = datetime.timedelta(0, 0)
            one.save()
        else:
            for dt in daterange(one.entry_time.astimezone(local_tz), one.leaving_time.astimezone(local_tz)):
                if dt.weekday() not in {5, 6}:
                    totalHolidays += datetime.timedelta(days=1)
            one.total_time = totalHolidays
            one.extra_time = datetime.timedelta(0, 0)
            one.save()
    return HttpResponseRedirect(previous_page)


@permission_required('hr_working_hours.change_workinghours')
def time_diff(request, user, week_start, week_end):
    previous_page = request.META.get('HTTP_REFERER')
    start = datetime.datetime.combine(datetime.datetime.strptime(week_start, "%d-%m-%Y"), datetime.time(0, 0))
    end = datetime.datetime.combine(datetime.datetime.strptime(week_end, "%d-%m-%Y"), datetime.time(23, 59))
    working_time = WorkingHours.objects.filter(Q(shortsign=user), Q(entry_time__range=[start, end]))
    find_bhp = HolidayTypes.objects.get(type='BHP')
    local_tz = pytz.timezone('Europe/Warsaw')
    for one in working_time:
        totalHolidays = datetime.timedelta(days=0)
        if not one.holiday:
            if one.leaving_time and one.entry_time:
                if (one.leaving_time - one.entry_time) > datetime.timedelta(hours=8):
                    one.total_time = datetime.timedelta(hours=8)
                    one.extra_time = datetime.timedelta(0, (((((one.leaving_time - one.entry_time)
                                                               - datetime.timedelta(hours=8)).seconds/60)/30)*30)*60)
                    if one.extra_time > datetime.timedelta(hours=4):
                        one.extra_time = datetime.timedelta(hours=4)
                    one.save()
                else:
                    one.total_time = one.leaving_time - one.entry_time
                    one.extra_time = datetime.timedelta(0, 0)
                    one.save()
        if one.holiday and one.leaving_time and one.entry_time and one.holiday_type_id != find_bhp.id:
            if one.leaving_time.date() == one.entry_time.date():
                one.total_time = datetime.timedelta(days=1)
                one.extra_time = datetime.timedelta(0, 0)
                one.save()
            else:
                for dt in daterange(one.entry_time.astimezone(local_tz), one.leaving_time.astimezone(local_tz)):
                    if dt.weekday() not in {5, 6}:
                        totalHolidays += datetime.timedelta(days=1)
                one.total_time = totalHolidays
                one.extra_time = datetime.timedelta(0, 0)
                one.save()
        if one.holiday and one.leaving_time and one.entry_time and one.holiday_type_id == find_bhp.id:
            if one.leaving_time.date() == one.entry_time.date():
                one.total_time = datetime.timedelta(hours=8)
                one.extra_time = datetime.timedelta(0, 0)
                one.save()
            else:
                for dt in daterange(one.entry_time.astimezone(local_tz), one.leaving_time.astimezone(local_tz)):
                    if dt.weekday() not in {5, 6}:
                        totalHolidays += datetime.timedelta(days=1)
                one.total_time = totalHolidays
                one.extra_time = datetime.timedelta(0, 0)
                one.save()
    return HttpResponseRedirect(previous_page)


@permission_required('hr_working_hours.change_workinghours')
def zero_extra_hours(request, user, week_start, week_end):
    previous_page = request.META.get('HTTP_REFERER')
    start = datetime.datetime.combine(datetime.datetime.strptime(week_start, "%d-%m-%Y"), datetime.time(0, 0))
    end = datetime.datetime.combine(datetime.datetime.strptime(week_end, "%d-%m-%Y"), datetime.time(23, 59))
    working_time = WorkingHours.objects.filter(Q(shortsign=user), Q(entry_time__range=[start, end]))
    for n in working_time:
        n.extra_time = datetime.timedelta(0)
        n.save()
    return HttpResponseRedirect(previous_page)


@permission_required('hr_working_hours.change_workinghours')
def zero_extra_hours_inline(request, pk):
    previous_page = request.META.get('HTTP_REFERER')
    WorkingHours.objects.filter(pk=pk).update(extra_time=datetime.timedelta(0))
    return HttpResponseRedirect(previous_page)


@permission_required('hr_working_hours.change_workinghours')
def accept_entry_inline(request, pk):
    decision = WorkingHours.objects.get(pk=pk).accepted
    previous_page = request.META.get('HTTP_REFERER')
    if decision:
        WorkingHours.objects.filter(pk=pk).update(accepted_by=None, accepted=False)
    else:
        WorkingHours.objects.filter(pk=pk).update(accepted_by=request.user.username, accepted=True)
    return HttpResponseRedirect(previous_page)


@permission_required('hr_working_hours.change_workinghours')
def create_entry_inline(request, entry_date, entry_time, worker):
    day, month, year = entry_date.split('-')
    hour, minutes = entry_time.split(':')
    start = datetime.datetime(int(year), int(month), int(day), int(hour), int(minutes))
    stop = start + datetime.timedelta(hours=8)
    WorkingHours.objects.create(
        entry_time=start, leaving_time=stop, shortsign=worker, accepted=True, accepted_by=request.user.username)
    previous_page = request.META.get('HTTP_REFERER')
    return HttpResponseRedirect(previous_page)


@permission_required('hr_working_hours.change_workinghours')
def change_entry_inline(request, pk, start_time):
    hour, minutes = start_time.split(':')
    start = datetime.time(int(hour), int(minutes))
    entry = WorkingHours.objects.get(pk=pk)
    entry.entry_time = datetime.datetime.combine(entry.entry_time.date(), start)
    entry.save()
    previous_page = request.META.get('HTTP_REFERER')
    return HttpResponseRedirect(previous_page)


@permission_required('hr_working_hours.change_workinghours')
def change_leaving_inline(request, pk, stop_time):
    hour, minutes = stop_time.split(':')
    stop = datetime.time(int(hour), int(minutes))
    entry = WorkingHours.objects.get(pk=pk)
    if stop != datetime.time(5, 45):
        entry.leaving_time = datetime.datetime.combine(entry.entry_time.date(), stop)
    else:
        if not entry.leaving_time:
            entry.leaving_time = datetime.datetime.combine(entry.entry_time.date() + datetime.timedelta(days=1), stop)
        if entry.entry_time.date() == entry.leaving_time.date():
            entry.leaving_time = datetime.datetime.combine(entry.leaving_time.date() + datetime.timedelta(days=1), stop)
        else:
            entry.leaving_time = datetime.datetime.combine(entry.leaving_time.date(), stop)
    entry.save()
    previous_page = request.META.get('HTTP_REFERER')
    return HttpResponseRedirect(previous_page)


# last day #
@permission_required('hr_working_hours.add_lastday')
def last_day_list(request):
    allDays = LastDay.objects.all()
    return HttpResponse(loader.get_template('last_day_list.html').render({'all': allDays}, request))


@permission_required('hr_working_hours.add_lastday')
def last_day_create(request):
    template = loader.get_template('last_day_create.html')
    next = request.POST.get('next', '/')
    previous_page = request.META.get('HTTP_REFERER')
    last_days = LastDay.objects.all()
    workers = User.objects.filter(~Q(usercompanycard__company__name='apprentice'),
                                  ~Q(username='deleted'),
                                  ~Q(groups__name__icontains='managers'))
    workers_diff = []
    for all in workers:
        found = False
        for sub in last_days:
            if sub.worker_id == all.id:
                found = True
                break
        if not found:
            workers_diff.append(all)
    form = LastDayForm(request.POST)
    if form.is_valid():
        form.save()
        if form.cleaned_data['first_day']:
            first_day_training(request, form.cleaned_data['worker'], form.cleaned_data['first_day'])
        return HttpResponseRedirect(next)
    else:
        form = LastDayForm()
    context = {'form': form, 'previous_page': previous_page, 'next': next, 'workers_diff': workers_diff}
    return HttpResponse(template.render(context, request))


@permission_required('hr_working_hours.change_lastday')
def last_day_edit(request, pk):
    template = loader.get_template('last_day_edit.html')
    edit = LastDay.objects.get(pk=pk)
    next = request.POST.get('next', '/')
    previous_page = request.META.get('HTTP_REFERER')
    last_days = LastDay.objects.all()
    workers = User.objects.filter(~Q(usercompanycard__company__name='apprentice'),
                                  ~Q(username='deleted'))
    workers_diff = []
    for all in workers:
        found = False
        for sub in last_days:
            if sub.worker_id == all.id:
                found = True
                break
        if not found:
            workers_diff.append(all)
    if request.method == "POST":
        form = LastDayForm(request.POST, instance=edit)
        if form.is_valid():
            form.save()
            first_day_training(request, form.cleaned_data['worker'], form.cleaned_data['first_day'])
        return HttpResponseRedirect(next)
    else:
        form = LastDayForm(instance=edit)
        context = {'form': form, 'previous_page': previous_page, 'next': next, 'edit': edit,
                   'workers_diff': workers_diff}
        return HttpResponse(template.render(context, request))


@permission_required('hr_working_hours.delete_lastday')
def last_day_delete(request, pk):
    previous_page = request.META.get('HTTP_REFERER')
    item = LastDay.objects.get(pk=pk).delete()
    if request.method == 'POST':
        form = LastDayForm(request.POST, instance=item)
        form.u.delete()
        form.save()
    return HttpResponseRedirect(previous_page)


@permission_required('hr_working_hours.change_lastday')
def first_day_training(request, worker, first_day):
    training_id, cr = HolidayTypes.objects.get_or_create(type="BHP")
    if WorkingHours.objects.filter(shortsign=worker, holiday_type=training_id.id).exists():
        WorkingHours.objects.filter(shortsign=worker, holiday_type=training_id.id).update(
            entry_time=datetime.datetime.combine(first_day,
                                                 datetime.datetime.strptime('0800', '%H%M').time()),
            leaving_time=datetime.datetime.combine(first_day, datetime.datetime.strptime('1600', '%H%M').time()),
            holiday=True, holiday_type_id=training_id.id)
    else:
        WorkingHours.objects.create(shortsign=worker,
                                    entry_time=datetime.datetime.combine(
                                        first_day, datetime.datetime.strptime('0800', '%H%M').time()),
                                    leaving_time=datetime.datetime.combine(
                                        first_day, datetime.datetime.strptime('1600', '%H%M').time()),
                                    holiday=True, holiday_type_id=training_id.id
                                    )


@permission_required('hr_working_hours.view_manager_to_worker')
def managers_workers_add(request):
    template = loader.get_template('managers_workers_add.html')
    form = ManagerToWorkersGroupForm(request.POST)
    users_assigned = ManagerToWorker.objects.all()
    managers = User.objects.filter(groups__name__icontains='managers')
    workers = User.objects.filter(~Q(usercompanycard__company__name='apprentice'), ~Q(username='deleted'))
    managers_diff = []
    workers_diff = []
    for all in workers:
        found = False
        for sub in users_assigned:
            if sub.worker_id == all.id:
                found = True
                break
        if not found:
            workers_diff.append(all)
    for all in managers:
        found = False
        for sub in users_assigned:
            if sub.manager_id == all.id:
                found = True
                break
        if not found:
            managers_diff.append(all)
    if form.is_valid():
        for n in request.POST.getlist('workers'):
            ManagerToWorker.objects.create(manager=form.cleaned_data['manager'], worker_id=n)
    context = {'form': form, 'workers_diff': workers_diff, 'managers_diff': managers_diff}
    return HttpResponse(template.render(context, request))


@permission_required('hr_working_hours.change_managertoworker')
def managers_workers_edit(request, worker_id):
    template = loader.get_template('managers_workers_edit.html')
    next = request.POST.get('next', '/')
    previous_page = request.META.get('HTTP_REFERER')
    get_id = ManagerToWorker.objects.get(worker_id=worker_id)
    edit = ManagerToWorker.objects.get(id=get_id.id)
    users_assigned = ManagerToWorker.objects.all()
    managers = User.objects.filter(groups__name__icontains='managers')
    managers_diff = []
    for all in managers:
        found = False
        for sub in users_assigned:
            if sub.manager_id == all.id:
                found = True
                break
        if not found:
            managers_diff.append(all)
    if request.method == 'POST':
        form = ManagerToWorkerForm(request.POST, instance=edit)
        if form.is_valid():
            return HttpResponseRedirect(next)
        else:
            form = ManagerToWorkerForm(instance=edit)
        context = {'form': form, 'managers_diff': managers_diff, 'edit': edit, 'previous_page': previous_page,
                   'next': next}
        return HttpResponse(template.render(context, request))


@permission_required('hr_working_hours.change_managertoworker')
def ManToWork(request, worker, manager):
    if ManagerToWorker.objects.filter(worker_id=worker):
        ManagerToWorker.objects.filter(worker_id=worker).update(manager_id=manager)
    else:
        ManagerToWorker.objects.create(worker_id=worker, manager_id=manager)
    url = reverse('canteen:user_companies_edit', kwargs={'pk': worker})
    return HttpResponseRedirect(url)


@permission_required('hr_working_hours.can_draw_report')
def download_csv(request, date_start, date_end, company):
    directory = BASE_DIR + '/hr_working_hours/reports/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    start = datetime.datetime.combine(datetime.datetime.strptime(date_start, "%d-%m-%Y"), datetime.time(0, 0))
    end = datetime.datetime.combine(datetime.datetime.strptime(date_end, "%d-%m-%Y"), datetime.time(23, 59))
    users = []
    employees = []
    company_name = Company.objects.get(id=company).name
    for n in User.objects.filter(Q(usercompanycard__company__id=company), Q(is_active=True)).values_list('username'):
        employees.append(n[0])
    entries = WorkingHours.objects.filter(Q(entry_time__range=[start, end]), Q(shortsign__in=employees)).values()
    for n in entries.distinct('shortsign'):
        users.append(n['shortsign'])
    for n in users:
        per_user = entries.filter(shortsign=n).order_by('entry_time')
        try:
            hours, remainder = divmod(entries.filter(Q(shortsign=n), Q(holiday=False)).aggregate(total_hours=Sum('total_time'))['total_hours'].total_seconds(), 60 * 60)
            minutes, seconds = divmod(remainder, 60)
        except:
            hours, remainder, minutes, seconds = 0, 0, 0, 0
        with open(BASE_DIR + '/hr_working_hours/reports/' + str(company_name) + str('_') + str(n) + '.csv', 'w')\
                as file:
            fieldnames = ['worker', 'entry', 'leave', 'holiday', 'holiday type', 'time', 'over hours']
            writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=str(';'))
            writer.writeheader()
            for x in per_user:
                now_timestamp = time.time()
                offset = datetime.datetime.fromtimestamp(now_timestamp) -\
                         datetime.datetime.utcfromtimestamp(now_timestamp)
                if x['entry_time']:
                    entry_time = (x['entry_time'] + offset).strftime("%d-%m-%Y %R")
                else:
                    entry_time = None
                if x['leaving_time']:
                    leaving_time = (x['leaving_time'] + offset).strftime("%d-%m-%Y %R")
                else:
                    leaving_time = None
                if x['holiday']:
                    x['holiday'] = 'yes'
                    x['holiday_type_id'] = HolidayTypes.objects.get(id=x['holiday_type_id']).type
                else:
                    x['holiday'] = 'no'
                writer.writerow({'worker': x['shortsign'], 'entry': entry_time, 'leave': leaving_time,
                                 'holiday': x['holiday'], 'holiday type': x['holiday_type_id'], 'time': x['total_time'],
                                 'over hours': x['extra_time']})
            file.write('\n')
            file.write('total working time: {} hours {} minutes\n'.format(hours, minutes))
    send_csv(request, company_name.encode())
    previous_page = request.META.get('HTTP_REFERER')
    return HttpResponseRedirect(previous_page)


def send_csv(request, company_name):
    try:
        recipient = str(request.user.email)
    except:
        recipient = str(request.user.username + '@viessmann.com')
    email_to = []
    email_to.append(recipient)
    day = str(datetime.date.today())
    subject = 'work time reports ' + company_name.decode('UTF-8') + ' ' + day
    msg = MIMEMultipart()
    email_sender = settings.EMAIL_HOST_USER
    msg['From'] = email_sender
    msg['To'] = ",".join(email_to)
    msg['Subject'] = subject
    body = 'mail'
    msg.attach(MIMEText(body, 'plain'))
    attachment_path_list = glob.glob(BASE_DIR + '/hr_working_hours/reports/*.csv')
    for each_file_path in attachment_path_list:
        try:
            file_name = each_file_path.split("/")[-1]
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(each_file_path, "rb").read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename=file_name)
            msg.attach(part)
        except:
            print("couldn't attach file")
    text = msg.as_string()
    email_send = email_to
    connection = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    connection.starttls()
    connection.login(email_sender, settings.EMAIL_HOST_PASSWORD)
    connection.sendmail(email_sender, email_send, text)
    connection.quit()
    url = reverse('hr_working_hours:hr_reports')
    return HttpResponseRedirect(url)


@permission_required('hr_working_hours.can_draw_report')
def company_serialize(request):
    all_companies = Company.objects.values('id', 'name')
    json_serializer = json.dumps(list(all_companies))
    return HttpResponse(json_serializer, content_type='application/json')


@permission_required('hr_working_hours.can_draw_report')
def location_serialize(request):
    all_locations = Location.objects.values()
    json_serializer = json.dumps(list(all_locations))
    return HttpResponse(json_serializer, content_type='application/json')\


@permission_required('hr_working_hours.can_draw_report')
def manager_serialize(request):
    all_managers = User.objects.filter(groups__name='managers').values('id', 'username')
    json_serializer = json.dumps(list(all_managers))
    return HttpResponse(json_serializer, content_type='application/json')
