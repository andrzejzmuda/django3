# -*- coding: utf-8 -*-
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .forms_users_addons import PersonalForm, CreateUserFormStage1, CreateUserFormStage2, CreateUserFormStage3
import json
import os
from django import template
from django.db.models import Q
from django.utils.crypto import get_random_string
from django.template import loader

from PIL import Image, ImageDraw, ImageFont

from django3_apps.settings import BASE_DIR
from canteen.models import UserCompanyCard, Company
from hr_working_hours.models import ManagerToWorker, LastDay
from hr_working_hours.views import first_day_training
from core.models_users_addons import Personal_number


register = template.Library()

@permission_required('canteen.add_usercompanycard')
def NewUserS1(request):
    template = loader.get_template('users_addons/NewUserS1.html')
    previous_page = request.META.get('HTTP_REFERER')
    if request.method == "POST":
        form = CreateUserFormStage1(request.POST)
        if form.is_valid():
            shortsign = form.cleaned_data['shortsign'].replace(" ", "_").replace("-", "_")
            company = form.cleaned_data['company']
            manager = form.cleaned_data['manager']
            pers_number = form.cleaned_data['pers_number']
            NewAccount(request, shortsign, manager)
            AddCompany(request, shortsign, company)
            if pers_number:
                AddPersNumber(request, shortsign, pers_number)
            return HttpResponseRedirect(reverse('core:NewUserS2', kwargs={'shortsign': shortsign}))
    else:
        form = CreateUserFormStage1()
        return HttpResponse(template.render({'form': form, 'previous_page': previous_page}, request))


@permission_required('canteen.add_usercompanycard')
def NewAccount(request, shortsign, manager):
    previous_page = request.META.get('HTTP_REFERER')
    new_user = User.objects.create_user(shortsign,
                                    password=get_random_string(length=32))
    new_user.is_superuser = False
    new_user.is_staff = False
    new_user.save()
    try:
        client_group = Group.objects.get(name='stolowka_klient')
    except:
        client_group = Group.objects.create(name='stolowka_klient')
    client_group.user_set.add(new_user)
    ManagerToWorker.objects.create(worker_id=new_user.id, manager_id=User.objects.get(username=manager).id).save()
    return HttpResponseRedirect(previous_page)


@permission_required('canteen.add_usercompanycard')
def AddCompany(request, shortsign, company):
    previous_page = request.META.get('HTTP_REFERER')
    new_user_id = User.objects.get(username=shortsign).id
    company_name = str(company).rsplit(' ', 1)[0]
    UserCompanyCard.objects.filter(user_id=new_user_id).update(company_id=Company.objects.get(name=company_name).id)
    return HttpResponseRedirect(previous_page)


@permission_required('core.add_personal_number')
def AddPersNumber(request, shortsign, pers_number):
    previous_page = request.META.get('HTTP_REFERER')
    new_user_id = User.objects.get(username=shortsign).id
    Personal_number.objects.create(user_id=new_user_id, pers_number=pers_number).save()
    return HttpResponseRedirect(previous_page)


@permission_required('canteen.add_usercompanycard')
def NewUserS2(request, shortsign):
    template = loader.get_template('users_addons/NewUserS2.html')
    if request.method == "POST":
        form = CreateUserFormStage2(request.POST)
        if form.is_valid():
            card = form.cleaned_data['card_original']
            SaveCard(request, card, shortsign)
        return HttpResponseRedirect(reverse('core:NewUserS3', kwargs={'shortsign': shortsign}))
    else:
        form = CreateUserFormStage2()
    return HttpResponse(template.render({'shortsign': shortsign, 'form': form}, request))


@permission_required('canteen.add_usercompanycard')
def SaveCard(request, card, shortsign):
    previous_page = request.META.get('HTTP_REFERER')
    new_user_id = User.objects.get(username=shortsign).id
    UserCompanyCard.objects.filter(user_id=new_user_id).update(card=card, card_original=card)
    return HttpResponseRedirect(previous_page)


@permission_required('canteen.add_usercompanycard')
def PrintCard(request, shortsign):
    previous_page = request.META.get('HTTP_REFERER')
    img = Image.new('RGB', (200, 150), color='white')
    d = ImageDraw.Draw(img)
    fnt = ImageFont.truetype('/static/core/fonts/Arial Bold.ttf', 30)
    d.text((20, 30), str(shortsign), font=fnt, fill=(0, 0, 0))
    d.text((20, 80), "Viessmann", font=fnt, fill=(0, 0, 0,))
    directory = BASE_DIR + '/core/templates/card/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    img.save(directory + 'card.jpg')
    image = Image.open(directory + 'card.jpg')
    image.show()
    return HttpResponseRedirect(previous_page)


@permission_required('canteen.add_usercompanycard')
def NewUserS3(request, shortsign):
    template = loader.get_template('users_addons/NewUserS3.html')
    new_user_id = User.objects.get(username=shortsign).id
    if request.method == 'POST':
        form = CreateUserFormStage3(request.POST)
        if form.is_valid():
            first_day = form.cleaned_data['first_day']
            last_day = form.cleaned_data['last_day']
            if first_day:
                SetLastDay(request, shortsign, last_day or None, first_day)
        return HttpResponseRedirect(reverse('hr_working_hours:hr_reports'))
    else:
        form = CreateUserFormStage3()
        context = {'shortsign': shortsign, 'form': form, 'new_user_id': new_user_id}
        return HttpResponse(template.render(context, request))


@permission_required('canteen.add_usercompanycard')
def SetLastDay(request, shortsign, last_day, first_day):
    previous_page = request.META.get('HTTP_REFERER')
    new_user_id = User.objects.get(username=shortsign).id
    LastDay.objects.create(worker_id=new_user_id, last_day=last_day, first_day=first_day).save()
    first_day_training(request, shortsign, first_day)
    return HttpResponseRedirect(previous_page)


@permission_required('core.change_personal_number')
def pers_numbers(request):
    users = User.objects.filter(~Q(usercompanycard__company__name='apprentice'))
    pers_numbers = Personal_number.objects.all()
    diff = []
    template = loader.get_template('users_addons/pers_numbers.html')
    for all in users:
        found = False
        for sub in pers_numbers:
            if sub.user_id == all.id:
                found = True
                break
        if not found:
            diff.append(all)
    if request.method == 'GET':
        form = PersonalForm()
    elif request.method == 'POST':
        form = PersonalForm(request.POST)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse('core:pers_numbers'))
    else:
        form = PersonalForm()
    context = {'users': users, 'form': form, 'diff': diff, 'pers_numbers': pers_numbers}
    return HttpResponse(template.render(context, request))


@permission_required('core.add_personal_number')
def edit_pers_number(request, pk):
    edit = Personal_number.objects.get(id=pk)
    template = loader.get_template('users_addons/edit_pers_number.html')
    if request.method == "POST":
        form = PersonalForm(request.POST, instance=edit)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse('core:pers_numbers'))
    else:
        form = PersonalForm(instance=edit)
        return HttpResponse(template.render({'edit': edit, 'form': form}, request))


@permission_required('core.delete_personal_number')
def delete_pers_number(request, pk):
    delete = Personal_number.objects.get(id=pk).delete()
    if request.method == "POST":
        form = PersonalForm(request.POST, instance=delete)
        if form.is_valid():
            form.u.delete()
            form.save()
    return HttpResponseRedirect(reverse('core:pers_numbers'))


@permission_required('core.change_personal_number')
def users_serialize(request):
    all_users = User.objects.values('id', 'username')
    json_serializer = json.dumps(list(all_users))
    return HttpResponse(json_serializer, content_type='application/json')


@permission_required('core.change_personal_number')
def users_temp_serialize(request):
    all_users = User.objects.filter(~Q(usercompanycard__company__name='Viessmann')).values('id', 'username')
    json_serializer = json.dumps(list(all_users))
    return HttpResponse(json_serializer, content_type='application/json')
