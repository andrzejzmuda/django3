# -*- coding: utf-8 -*-
from django.template import loader
from canteen.models import Menu, Order, Product, OrderItems, UserCompanyCard, Company, OrderConsents
from django.contrib.auth.models import User, Group
from django.utils.crypto import get_random_string
from core.models_users_addons import Personal_number, Consent
from canteen.forms import MenuForm, OrderForm, ProductForm, UserCompanyCardForm, CompanyForm, CreateUserForm, \
    ConsentForm
from django.shortcuts import get_object_or_404, reverse
from django.forms import inlineformset_factory
from django.http import HttpResponse, HttpResponseRedirect
import datetime
from django.db.models import Q, Sum, F, DecimalField, When, Case, Value
import json
from django import template
import csv
from django.contrib.auth.decorators import permission_required, login_required
import re
from django.utils.http import urlquote
from operator import itemgetter

from hr_working_hours.models import LastDay, ManagerToWorker
from hr_working_hours.forms import ManagerToWorkerForm


register = template.Library()


@login_required()
def users_admin(request):
    template = loader.get_template('canteen/users_admin.html')
    return HttpResponse(template.render({}, request))


@permission_required('canteen.add_company')
def companies(request):
    template = loader.get_template('canteen/companies.html')
    companies = Company.objects.values('id', 'name', 'discount')
    form = CompanyForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('canteen:companies'))
    else:
        form = CompanyForm(request.POST)
        return HttpResponse(template.render({'form': form, 'companies': companies}, request))


@permission_required('canteen.change_company')
def company_edit(request, pk):
    edit = get_object_or_404(Company, pk=pk)
    template = loader.get_template('canteen/company_edit.html')
    form = CompanyForm(request.POST, instance=edit)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('canteen:companies'))
        else:
            form = CompanyForm(instance=edit)
    return HttpResponse(template.render({'form': form, 'edit': edit}, request))


@permission_required('canteen.delete_company')
def company_delete(request, pk):
    item = get_object_or_404(Company, pk=pk).delete()
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=item)
        form.u.delete()
        form.save()
    return HttpResponseRedirect(reverse('canteen:companies'))


@permission_required('canteen.add_usercompanycard')
def users_company(request):
    users = User.objects.filter(Q(groups__name__contains='canteen'))
    duplicate = 0
    duplicate_name = 0
    template = loader.get_template('canteen/users_companies.html')
    form = CreateUserForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            if User.objects.filter(Q(username=form.cleaned_data['shortsign'])):
                duplicate = 1
                duplicate_name = User.objects.get(Q(username=form.cleaned_data['shortsign']))
                return HttpResponse(template.render({'users': users, 'form': form, 'duplicate': duplicate,
                                                     'duplicate_name': duplicate_name}, request))
            if Personal_number.objects.filter(Q(pers_number=form.cleaned_data['pers_number'])):
                duplicate = 1
                duplicate_pers_number = Personal_number.objects.get(pers_number=form.cleaned_data['pers_number'])
                return HttpResponse(template.render({'users': users, 'form': form, 'duplicate': duplicate,
                                                     'duplicate_pers_number': duplicate_pers_number}, request))
            if UserCompanyCard.objects.filter(Q(card=form.cleaned_data['card'])):
                duplicate = 1
                duplicate_card_number = UserCompanyCard.objects.get(card=form.cleaned_data['card'])
                return HttpResponse(template.render({'users': users, 'form': form, 'duplicate': duplicate,
                                                     'duplicate_card_number': duplicate_card_number}, request))
            new_user = User.objects.create_user(form.cleaned_data['shortsign'],
                                                password=get_random_string(length=32))
            new_user.is_superuser = False
            new_user.is_staff = False
            new_user.save()
            client_group = Group.objects.get(name='canteen_client')
            client_group.user_set.add(new_user)
            company_name = str(form.cleaned_data['company']).rsplit(' ', 1)[0]
            print(company_name)
            card_number = UserCompanyCard.objects.filter(user_id=new_user.id)
            card_number.update(card=form.cleaned_data['card'], card_original=form.cleaned_data['card'],
                               company_id=Company.objects.get(
                                   name=company_name).id)
            if form.cleaned_data['pers_number'] != '':
                Personal_number.objects.create(user_id=new_user.id, pers_number=form.cleaned_data['pers_number'])
                if form.cleaned_data['last_day']:
                    LastDay.objects.create(worker_id=new_user.id, last_day=form.cleaned_data['last_day'])
                return HttpResponseRedirect('/users_company/')
        else:
            form = CreateUserForm(request.POST)
    return HttpResponse(template.render({'users': users, 'form': form, 'duplicate': duplicate,
                                         'duplicate_name': duplicate_name}, request))


@permission_required('canteen.delete_usercompanycard')
def user_delete(request, id):
    item = get_object_or_404(UserCompanyCard, pk=id).delete()
    if request.method == 'POST':
        form = UserCompanyCardForm(request.POST, instance=item)
        form.u.delete()
        form.save()
    return HttpResponseRedirect('/users_company/')


@permission_required('canteen.change_usercompanycard')
def user_companies_edit(request, pk):
    template = loader.get_template('canteen/users_companies_edit.html')
    next = request.POST.get('next', '/')
    previous_page = request.META.get('HTTP_REFERER')
    user = User.objects.get(id=pk)
    form = CreateUserForm(request.POST)
    managerList = ManagerToWorkerForm()
    get_manager = ManagerToWorker.objects.filter(worker_id=pk)
    duplicate = 0
    duplicate_name = 0
    duplicate_pers_number = 0
    active_passive = user.is_active
    try:
        pers_number = Personal_number.objects.get(user_id=pk).pers_number
    except:
        pers_number = ''
    try:
        company = UserCompanyCard.objects.get(user=pk)
    except:
        company = ''
    try:
        last_day = LastDay.objects.get(worker=pk)
    except:
        last_day = ''
    if request.method == 'POST':
        if form.is_valid():
            if User.objects.filter(Q(username=form.cleaned_data['shortsign']), ~Q(id=user.id)):
                duplicate = 1
                duplicate_name = User.objects.get(Q(username=form.cleaned_data['shortsign']))
                context = {'user': user, 'form': form, 'duplicate': duplicate, 'pers_number': pers_number,
                           'company': company, 'duplicate_name': duplicate_name, 'active_passive': active_passive,
                           'last_day': last_day, 'managerList': managerList, 'get_manager': get_manager}
                return HttpResponse(template.render(context, request))
            if Personal_number.objects.filter(Q(pers_number=form.cleaned_data['pers_number']), ~Q(user_id=user.id)):
                duplicate = 1
                duplicate_pers_number = Personal_number.objects.get(pers_number=form.cleaned_data['pers_number'])
                context = {'user': user, 'form': form, 'pers_number': pers_number, 'company': company,
                           'duplicate': duplicate, 'duplicate_pers_number': duplicate_pers_number,
                           'active_passive': active_passive, 'last_day': last_day, 'managerList': managerList,
                           'get_manager': get_manager}
                return HttpResponse(template.render(context, request))
            if UserCompanyCard.objects.filter(Q(card=form.cleaned_data['card']), ~Q(user_id=user.id),
                                              Q(card__isnull=False)):
                duplicate = 1
                duplicate_card_number = UserCompanyCard.objects.get(card=form.cleaned_data['card'])
                context = {'user': user, 'form': form, 'pers_number': pers_number, 'company': company,
                           'duplicate': duplicate, 'duplicate_card_number': duplicate_card_number,
                           'active_passive': active_passive, 'last_day': last_day, 'managerList': managerList,
                           'get_manager': get_manager}
                return HttpResponse(template.render(context, request))
            else:
                User.objects.filter(pk=pk).update(username=form.cleaned_data['shortsign'])
                if form.cleaned_data['pers_number'] != "":
                    try:
                        Personal_number.objects.create(user_id=pk, pers_number=form.cleaned_data['pers_number'])
                    except:
                        Personal_number.objects.filter(user_id=pk).update(pers_number=form.cleaned_data['pers_number'])
                if form.cleaned_data['pers_number'] == "":
                    Personal_number.objects.filter(user_id=pk).delete()
                else:
                    Personal_number.objects.filter(user_id=pk).update(pers_number=form.cleaned_data['pers_number'])

                client_group = Group.objects.get(name='canteen_client')
                if not Group.objects.filter(Q(user=user.id), Q(permissions__group__name='canteen_client')):
                    client_group.user_set.add(user)
                company_name = str(form.cleaned_data['company']).rsplit(' ', 1)[0]
                if UserCompanyCard.objects.filter(user_id=user):
                    card_number = UserCompanyCard.objects.filter(user_id=user.id)
                    card_number.update(card=form.cleaned_data['card'], card_original=form.cleaned_data['card_original'],
                                       temp_card_date=form.cleaned_data['temp_card_date'],
                                       company_id=Company.objects.get(name=company_name).id)
                else:
                    UserCompanyCard.objects.create(user_id=user.id, card=form.cleaned_data['card'],
                                                   company_id=Company.objects.get(name=company_name).id)
                if form.cleaned_data['last_day']:
                    if LastDay.objects.filter(worker_id=user.id):
                        last_day.last_day = form.cleaned_data['last_day']
                        last_day.save()
                    else:
                        LastDay.objects.create(worker_id=user.id, last_day=form.cleaned_data['last_day'])
                if not form.cleaned_data['last_day']:
                    LastDay.objects.filter(worker_id=user.id).delete()
                if form.cleaned_data['first_day']:
                    if LastDay.objects.filter(worker_id=user.id):
                        last_day.first_day = form.cleaned_data['first_day']
                        last_day.save()
                    else:
                        LastDay.objects.create(worker_id=user.id, first_day=form.cleaned_data['first_day'])
                if not form.cleaned_data['first_day']:
                    LastDay.objects.filter(worker_id=user.id).update(first_day=form.cleaned_data['first_day'])
                return HttpResponseRedirect(reverse('hr_working_hours:hr_reports'))
        else:
            form = CreateUserForm(request.POST)
    return HttpResponse(template.render({'user': user, 'form': form, 'pers_number': pers_number, 'company': company,
                                         'duplicate': duplicate, 'duplicate_name': duplicate_name,
                                         'duplicate_pers_number': duplicate_pers_number, 'last_day': last_day,
                                         'active_passive': active_passive, 'managerList': managerList,
                                         'get_manager': get_manager}, request))


@permission_required('canteen.change_usercompanycard')
def deactivate_user(request, pk):
    user = User.objects.get(id=pk)
    user.is_active = False
    user.save()
    url = reverse('canteen:user_companies_edit', kwargs={'pk': pk})
    return HttpResponseRedirect(url)


@permission_required('canteen.change_usercompanycard')
def activate_user(request, pk):
    user = User.objects.get(id=pk)
    user.is_active = True
    user.save()
    url = reverse('canteen:user_companies_edit', kwargs={'pk': pk})
    return HttpResponseRedirect(url, {'pk': user.id})


@permission_required('canteen.add_product')
def dishes_all(request):
    dishes = Product.objects.all()
    template = loader.get_template('canteen/dishes_all.html')
    if request.method == 'POST':
        prod_form = ProductForm(request.POST)
        if prod_form.is_valid():
            prod_form.save()
            return HttpResponseRedirect(reverse('canteen:dishes_all'))
    else:
        prod_form = ProductForm()
    return HttpResponse(template.render({'prod_form': prod_form, 'dishes': dishes}, request))


@permission_required('canteen.change_product')
def dishes_edit(request, pk):
    edit = get_object_or_404(Product, pk=pk)
    template = loader.get_template('canteen/dishes_edit.html')
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=edit)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('canteen:dishes_all'))
    else:
        form = ProductForm(instance=edit)
    return HttpResponse(template.render({'form': form, 'edit': edit}, request))


@permission_required('canteen.delete_product')
def dishes_delete(request, pk):
    dish = Product.objects.get(pk=pk)
    template = loader.get_template('canteen/dishes_delete.html')
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=dish)
        if form.is_valid():
            dish.delete()
            return HttpResponseRedirect(reverse('canteen:dishes_all'))
    else:
        form = ProductForm(instance=dish)
    return HttpResponse(template.render({'form': form, 'dish': dish}, request))


@permission_required('canteen.view_menu')
def menu_all(request):
    template = loader.get_template('canteen/menu.html')
    order_time = datetime.datetime.now()
    url = request.build_absolute_uri().rsplit('/', 1)[1]
    menu = Menu.objects.all()
    product = Product.objects.all()
    start_week = datetime.date.today() - datetime.timedelta(datetime.date.today().weekday())
    end_week = start_week + datetime.timedelta(6)
    today = datetime.date.today()
    monday = datetime.date.today() - datetime.timedelta(datetime.date.today().weekday())
    tuesday = monday + datetime.timedelta(1)
    wednesday = monday + datetime.timedelta(2)
    thursday = monday + datetime.timedelta(3)
    friday = monday + datetime.timedelta(4)
    monday_menu = Menu.objects.filter(Q(date__contains=monday))
    tuesday_menu = Menu.objects.filter(Q(date__contains=tuesday))
    wednesday_menu = Menu.objects.filter(Q(date__contains=wednesday))
    thursday_menu = Menu.objects.filter(Q(date__contains=thursday))
    friday_menu = Menu.objects.filter(Q(date__contains=friday))
    menu_form = MenuForm(request.POST)
    if request.method == 'POST':
        if menu_form.is_valid():
            try:
                Order.objects.get(date=menu_form.cleaned_data['date'], user=None)
                for n in request.POST.getlist('product'):
                    Menu.objects.create(date=menu_form.cleaned_data['date'], product_id=n)
            except:
                Order.objects.create(date=menu_form.cleaned_data['date'], user=None)
                for n in request.POST.getlist('product'):
                    Menu.objects.create(date=menu_form.cleaned_data['date'], product_id=n)
                menu_form.save()
                return HttpResponseRedirect(reverse('canteen:menu_all'))
            else:
                menu_form = MenuForm()
    return HttpResponse(template.render({'menu_form': menu_form, 'menu': menu, 'start_week': start_week,
                                         'end_week': end_week, 'monday_menu': monday_menu, 'tuesday_menu': tuesday_menu,
                                         'wednesday_menu': wednesday_menu, 'thursday_menu': thursday_menu,
                                         'friday_menu': friday_menu, 'monday': monday, 'tuesday': tuesday,
                                         'wednesday': wednesday, 'thursday': thursday, 'friday': friday, 'today': today,
                                         'product': product, 'url': url, 'order_time': order_time}, request))


@permission_required('canteen.view_menu')
def my_account(request):
    template = loader.get_template('canteen/my_account.html')
    today = datetime.date.today()
    this_month = datetime.date.today().month
    first = today.replace(day=1)
    last_month = first - datetime.timedelta(days=1)
    report_last_month = Order.objects.filter(Q(date__year=last_month.year), Q(date__month=last_month.month),
                                             Q(user_id=request.user.id))
    logged_user = request.user
    get_discount = int(re.findall('\d+',
                                  UserCompanyCard.objects.get(
                                      card=logged_user.usercompanycard.card).company.discount)[0]) * 0.01
    sum_up_last_month = report_last_month.values('date').annotate(
        per_order=Sum(F('orderitems__quantity') * (F('orderitems__product__product__price')),
                      output_field=DecimalField())) \
        .annotate(user_cost=Case(
        When(per_order__gt=30, then=(F('per_order') - (30 * get_discount))),
        When(per_order__lte=30, then=(F('per_order') * (1 - get_discount))),
        output_field=DecimalField(decimal_places=2))) \
        .annotate(company_cost=Case(
        When(per_order__gt=30, then=(Value(30 * get_discount))),
        When(per_order__lte=30,
             then=(Sum(((F('orderitems__quantity') * (F('orderitems__product__product__price'))) * get_discount)))),
        output_field=DecimalField(decimal_places=2)
    ))
    cost_last = sum_up_last_month.aggregate(user_monthly=Sum('user_cost', output_field=DecimalField(decimal_places=2)))
    company_last = sum_up_last_month.aggregate(
        company_user=Sum('company_cost', output_field=DecimalField(decimal_places=2)))
    total_last = sum_up_last_month.aggregate(total=Sum('per_order', output_field=DecimalField(decimal_places=2)))
    report_this_month = Order.objects.filter(Q(date__year=datetime.date.today().year), Q(date__month=this_month),
                                             Q(user_id=request.user.id), Q(orderitems__sold=True))
    sum_up = report_this_month.values('date').order_by('date').annotate(
        per_order=Sum(F('orderitems__quantity') * (F('orderitems__product__product__price')),
                      output_field=DecimalField())) \
        .annotate(user_cost=Case(
        When(per_order__gt=30, then=(F('per_order') - (30 * get_discount))),
        When(per_order__lte=30, then=(F('per_order') * (1 - get_discount))),
        output_field=DecimalField(decimal_places=2))) \
        .annotate(company_cost=Case(
        When(per_order__gt=30, then=(Value(30 * get_discount))),
        When(per_order__lte=30,
             then=(Sum(((F('orderitems__quantity') * (F('orderitems__product__product__price'))) * get_discount)))),
        output_field=DecimalField(decimal_places=2)))
    cost = sum_up.aggregate(user_monthly=Sum('user_cost', output_field=DecimalField(decimal_places=2)))
    company = sum_up.aggregate(company_user=Sum('company_cost', output_field=DecimalField(decimal_places=2)))
    total = sum_up.aggregate(total=Sum('per_order', output_field=DecimalField(decimal_places=2)))
    context = {'sum_up_last_month': sum_up_last_month, 'cost_last': cost_last, 'company_last': company_last,
               'total_last': total_last, 'today': today, 'report_this_month': report_this_month, 'sum_up': sum_up,
               'cost': cost, 'company': company, 'total': total, 'last_month': last_month, 'get_discount': get_discount}
    return HttpResponse(template.render(context, request))


@permission_required('canteen.view_menu')
def next_week_menu(request):
    template = loader.get_template('canteen/menu.html')
    order_time = datetime.datetime.now()
    url = request.build_absolute_uri().rsplit('/', 1)[1]
    menu = Menu.objects.all()
    product = Product.objects.all()
    today = datetime.date.today()
    next_start = today + datetime.timedelta(days=-today.weekday(), weeks=1)
    next_end = next_start + datetime.timedelta(6)
    next_monday = next_start
    next_tuesday = next_monday + datetime.timedelta(1)
    next_wednesday = next_monday + datetime.timedelta(2)
    next_thursday = next_monday + datetime.timedelta(3)
    next_friday = next_monday + datetime.timedelta(4)
    next_monday_menu = Menu.objects.filter(Q(date__contains=next_monday))
    next_tuesday_menu = Menu.objects.filter(Q(date__contains=next_tuesday))
    next_wednesday_menu = Menu.objects.filter(Q(date__contains=next_wednesday))
    next_thursday_menu = Menu.objects.filter(Q(date__contains=next_thursday))
    next_friday_menu = Menu.objects.filter(Q(date__contains=next_friday))
    menu_form = MenuForm(request.POST)
    if request.method == 'POST':
        if menu_form.is_valid():
            try:
                Order.objects.get(date=menu_form.cleaned_data['date'], user=None)
                for n in request.POST.getlist('product'):
                    Menu.objects.create(date=menu_form.cleaned_data['date'], product_id=n)
            except:
                Order.objects.create(date=menu_form.cleaned_data['date'], user=None)
                for n in request.POST.getlist('product'):
                    Menu.objects.create(date=menu_form.cleaned_data['date'], product_id=n)
                return HttpResponseRedirect(reverse('canteen:next_week_menu'), {})
            else:
                menu_form = MenuForm()
    return HttpResponse(template.render({'menu_form': menu_form, 'menu': menu, 'start_week': next_start,
                                         'end_week': next_end, 'monday_menu': next_monday_menu,
                                         'tuesday_menu': next_tuesday_menu, 'wednesday_menu': next_wednesday_menu,
                                         'thursday_menu': next_thursday_menu, 'friday_menu': next_friday_menu,
                                         'monday': next_monday, 'tuesday': next_tuesday,
                                         'wednesday': next_wednesday, 'thursday': next_thursday,
                                         'friday': next_friday, 'today': today, 'product': product, 'url': url,
                                         'order_time': order_time}, request))


@permission_required('canteen.delete_menu')
def menu_delete(request, pk):
    template = loader.get_template('canteen/menu_delete.html')
    menu_item = Menu.objects.get(id=pk)
    base_items = OrderItems.objects.filter(Q(product=menu_item.product_id), Q(order__date=menu_item.date),
                                           Q(quantity=0))
    next = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        form = MenuForm(request.POST, instance=menu_item)
        if form.is_valid():
            base_items.delete()
            menu_item.delete()
            return HttpResponseRedirect(next)
    else:
        form = MenuForm(instance=menu_item)
    return HttpResponse(template.render({'form': form, 'menu_item': menu_item, 'next': next}, request))


@permission_required('canteen.add_order')
def order(request, date):
    template = loader.get_template('canteen/order.html')
    too_late_template = loader.get_template('canteen/too_late.html')
    try:
        new_order = get_object_or_404(Order, date=date, user_id=request.user.id)
    except:
        new_order = get_object_or_404(Order, date=date, user_id=None)
    orderformset = inlineformset_factory(Order, OrderItems, extra=1, fields='__all__', can_delete=True)
    try:
        consentText = Consent.objects.get(app='Canteen')
    except:
        newConsent = Consent.objects.create(
            consent='I hereby consent to deduct the price of my order from my next salary.', app='Canteen'
        )
        newConsent.save()
        consentText = Consent.objects.get(app='Canteen')
    try:
        consentAnswer = OrderConsents.objects.get(order_id=new_order.id).answer
    except:
        consentAnswer = False
    ordering_user = request.user
    next = request.POST.get('next', '/')
    consentForm = ConsentForm(request.POST)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=new_order)
        formset = orderformset(request.POST, instance=new_order)
        if form.is_valid():
            if formset.is_valid():
                if datetime.datetime.now() < datetime.datetime.combine(datetime.datetime.strptime(date, "%Y-%m-%d"),
                                                                       datetime.time(9, 30)):
                    try:
                        create_order = get_object_or_404(Order, date=date, user_id=request.user.id)
                        if consentForm.is_valid():
                            OrderConsents.objects.filter(Q(order_id=create_order.id), Q(consent_id=consentText.id)) \
                                .update(consent_id=consentText.id, answer=consentForm.cleaned_data['answer'])
                    except:
                        create_order = Order.objects.create(date=form.cleaned_data['date'], user_id=request.user.id)
                        if consentForm.is_valid():
                            OrderConsents.objects.create(order_id=create_order.id,
                                                         consent_id=consentText.id,
                                                         answer=consentForm.cleaned_data['answer']).save()
                    new = formset.save()
                    for n in new:
                        if n.quantity != 0:
                            n.order_id = create_order.id
                            n.sold = True
                            n.save()
                            create_order.save()
                    return HttpResponseRedirect(next)
                else:
                    return HttpResponse(too_late_template.render({}, request))
    else:
        form = OrderForm(instance=new_order)
        formset = orderformset(instance=new_order)
        for n in formset:
            n.fields['product'].queryset = Menu.objects.filter(date=date)
    return HttpResponse(template.render({'new_order': new_order, 'form': form, 'formset': formset,
                                         'ordering_user': ordering_user, 'date': date, 'consentForm': consentForm,
                                         'consentText': consentText, 'consentAnswer': consentAnswer}, request))


@permission_required('canteen.diner_front')
def diner_front(request):
    template = loader.get_template('canteen/diner_front.html')
    if request.method == 'POST':
        search_id = request.POST.get('textfield', None)
        try:
            card = UserCompanyCard.objects.get(card=search_id).card
            url = reverse('canteen:show_order', kwargs={'card': card})
            return HttpResponseRedirect(url)
        except UserCompanyCard.DoesNotExist:
            return HttpResponse(template.render({}, request))
    else:
        return HttpResponse(template.render({}, request))


@permission_required('canteen.diner_front')
def show_order(request, card):
    template = loader.get_template('canteen/show_order.html')
    username = User.objects.get(usercompanycard__card=card).username
    get_discount = int(re.findall('\d+', UserCompanyCard.objects.get(card=card).company.discount)[0]) * 0.01
    order = Order.objects.filter(Q(date=datetime.date.today()), Q(user__usercompanycard__card=card), Q(complete=False)) \
        .values('orderitems__product__product__name', 'orderitems__product__product__price', 'orderitems__quantity',
                'orderitems__product__product_id', 'orderitems__id', 'orderitems__sold').order_by('-orderitems__id')
    price = order.values('orderitems__order__date').annotate(
        price=Sum(F('orderitems__quantity') * (F('orderitems__product__product__price')),
                  output_field=DecimalField())).annotate(
        user_cost=Case(
            When(price__gt=30, orderitems__sold=True, then=(F('price') - (30 * get_discount))),
            When(price__lte=30, orderitems__sold=True, then=(F('price') * (1 - get_discount))),
            output_field=DecimalField(decimal_places=2))) \
        .aggregate(user_cost_total=Sum('user_cost', output_field=DecimalField(max_digits=4, decimal_places=2)))
    context = {'order': order, 'price': price, 'card': card, 'username': username, 'get_discount': get_discount * 100}
    return HttpResponse(template.render(context, request))


@permission_required('canteen.diner_front')
def sold_unsold(request, pk):
    OrderItems.objects.filter(pk=pk).update(sold=Case(
        When(sold=False, then=True),
        When(sold=True, then=False))
    )
    previous_page = request.META.get('HTTP_REFERER')
    return HttpResponseRedirect(previous_page)


@permission_required('canteen.diner_front')
def change_quantity(request, pk, operator):
    item = OrderItems.objects.filter(pk=pk)
    if operator == "plus":
        item.update(quantity=F('quantity') + 1)
    if operator == "minus":
        item.update(quantity=F('quantity') - 1)
    previous_page = request.META.get('HTTP_REFERER')
    return HttpResponseRedirect(previous_page)


@permission_required('canteen.diner_front')
def close_order(request, card):
    Order.objects.filter(Q(date=datetime.date.today()), Q(user__usercompanycard__card=card), Q(complete=False)).update(
        complete=True)
    url = reverse('canteen:diner_front')
    return HttpResponseRedirect(url)


@permission_required('canteen.diner_front')
def how_many_left(request):
    template = loader.get_template('canteen/how_many_left.html')
    today = datetime.date.today()
    dishes = OrderItems.objects.filter(Q(order__date=today), Q(order__complete=False), ~Q(quantity__isnull=True),
                                       ~Q(quantity=0),
                                       Q(product__isnull=False)).distinct().values('product__product__name')
    dishes_list = dishes.distinct().annotate(quantity=Sum(F('quantity')))
    context = {'today': today, 'dishes_list': dishes_list}
    return HttpResponse(template.render(context, request))


@permission_required('canteen.draw_report')
def reports(request):
    return HttpResponse(loader.get_template('canteen/reports.html').render({}, request))


@permission_required('canteen.draw_report')
def report_per_company(request, from_date, to_date, company):
    strfrom = datetime.datetime.strptime(from_date, "%d-%m-%Y")
    strto = datetime.datetime.strptime(to_date, "%d-%m-%Y")
    get_discount = int(re.findall('\d+', Company.objects.get(id=company).discount)[0]) * 0.01
    report = OrderItems.objects.filter(Q(order__date__range=(strfrom, strto)), Q(order__complete=True), Q(sold=True),
                                       ~Q(order__user_id=None), ~Q(product_id=None), ~Q(quantity=0),
                                       Q(order__user__usercompanycard__company_id=company))
    per_company = report.values('order__user_id', 'order__date').annotate(
        per_order=Sum(F('quantity') * (F('product__product__price')), output_field=DecimalField())) \
        .annotate(user_cost=Case(
        When(per_order__gt=30, then=(F('per_order') - (30 * get_discount))),
        When(per_order__lte=30, then=(F('per_order') * (1 - get_discount))),
        output_field=DecimalField(decimal_places=2))) \
        .annotate(company_cost=Case(
        When(per_order__gt=30, then=(Value(((30 * get_discount)), output_field=DecimalField(decimal_places=2)))),
        When(per_order__lte=30, then=(Sum(((F('quantity') * (F('product__product__price'))) * get_discount)))),
        output_field=DecimalField(decimal_places=2)))
    company_monthly = per_company.values('company_cost').aggregate(
        company_monthly=Sum('company_cost', output_field=DecimalField(decimal_places=2)))
    template = loader.get_template('canteen/report_from_to.html')
    context = {'report': report, 'per_company': per_company, 'company': company, 'company_monthly': company_monthly,
               'from_date': from_date, 'to_date': to_date}
    return HttpResponse(template.render(context, request))


@permission_required('canteen.draw_report')
def report_per_company_csv(request, from_date, to_date, company):
    strfrom = datetime.datetime.strptime(from_date, "%d-%m-%Y")
    strto = datetime.datetime.strptime(to_date, "%d-%m-%Y")
    get_discount = int(re.findall('\d+', Company.objects.get(id=company).discount)[0]) * 0.01
    report = OrderItems.objects.filter(Q(order__date__range=(strfrom, strto)), Q(order__complete=True), Q(sold=True),
                                       ~Q(order__user_id=None), ~Q(product_id=None),
                                       ~Q(quantity=0), Q(order__user__usercompanycard__company_id=company))
    per_company = report.values('order__user__username', 'order__date').annotate(
        per_order=Sum(F('quantity') * (F('product__product__price')), output_field=DecimalField())) \
        .annotate(user_cost=Case(
        When(per_order__gt=30, then=(F('per_order') - (30 * get_discount))),
        When(per_order__lte=30, then=(F('per_order') * (1 - get_discount))), output_field=DecimalField())) \
        .annotate(company_cost=Case(
        When(per_order__gt=30, then=(Value((30 * get_discount), output_field=DecimalField(decimal_places=2)))),
        When(per_order__lte=30, then=(Sum(((F('quantity') * (F('product__product__price'))) * get_discount)))),
        output_field=DecimalField(decimal_places=2)))
    company_monthly = per_company.values('company_cost').aggregate(
        company_monthly=Sum('company_cost', output_field=DecimalField(decimal_places=2)))
    company_name = Company.objects.get(id=company).name
    response = HttpResponse(content_type='text/csv')
    filename = str(company_name) + '.csv'
    response['Content-Disposition'] = 'attachment; filename={}'.format(urlquote(filename))
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['date', 'client', 'personal number', '100% cost', "client's cost", 'discount cost'])
    for n in per_company:
        writer.writerow([n.get('order__date'), n.get('order__user__username'),
                         list(map(itemgetter(0), (Personal_number.objects.filter(
                             user_id__username=n.get('order__user__username')).values_list('pers_number')))),
                         n.get('per_order'), n.get('user_cost'), n.get('company_cost')])
    writer.writerow(['total monthly cost for:', company_name, company_monthly.get('company_monthly')])
    return response


@permission_required('canteen.draw_report')
def report_per_person(request, from_date, to_date, company):
    template = loader.get_template('canteen/report_per_person.html')
    strfrom = datetime.datetime.strptime(from_date, "%d-%m-%Y")
    strto = datetime.datetime.strptime(to_date, "%d-%m-%Y")
    get_discount = int(re.findall('\d+', Company.objects.get(id=company).discount)[0]) * 0.01
    report = OrderItems.objects.filter(Q(order__date__range=(strfrom, strto)),
                                       Q(order__user__usercompanycard__company_id=company), Q(order__complete=True),
                                       Q(sold=True), ~Q(order__user_id=None), ~Q(order__user_id=None))
    users = report.values('order__user_id').distinct()
    per_person = users.distinct().annotate(
        full_price=Sum(F('quantity') * (F('product__product__price')), output_field=DecimalField()))
    per_order = users.values('order_id').annotate(
        per_order=Sum(F('quantity') * (F('product__product__price')), output_field=DecimalField()))

    sum_up = users.values('order__user_id', 'order__date').annotate(
        per_order=Sum(F('quantity') * (F('product__product__price')), output_field=DecimalField())) \
        .annotate(user_cost=Case(
        When(per_order__gt=30, then=(F('per_order') - (30 * get_discount))),
        When(per_order__lte=30, then=(F('per_order') * (1 - get_discount))),
        output_field=DecimalField(decimal_places=2))) \
        .annotate(company_cost=Case(
        When(per_order__gt=30, then=(30 * get_discount)),
        When(per_order__lte=30, then=(Sum(((F('quantity') * (F('product__product__price'))) * get_discount)))),
        output_field=DecimalField(decimal_places=2)))
    user_cost = []
    for n in users:
        cost = sum_up.filter(order__user_id=n.get('order__user_id')).aggregate(
            user_monthly=Sum('user_cost', output_field=DecimalField(decimal_places=2)))
        company_monthly = sum_up.filter(order__user_id=n.get('order__user_id')).aggregate(
            company_user=Sum('company_cost', output_field=DecimalField(decimal_places=2)))
        total = sum_up.filter(order__user_id=n.get('order__user_id')).aggregate(
            total=Sum('per_order', output_field=DecimalField(decimal_places=2)))
        data = {
            'name': next(iter((n.values()))),
            'user_cost': next(iter((cost.values()))),
            'company': next(iter((company_monthly.values()))),
            'total': next(iter((total.values())))
            }
        user_cost.append(data)
        print(data)
    context = {'per_person': per_person, 'users': users, 'sum_up': sum_up, 'per_order': per_order, 'report': report,
               'user_cost': user_cost, 'from_date': from_date, 'to_date': to_date, 'company': company}
    return HttpResponse(template.render(context, request))


@permission_required('canteen.draw_report')
def report_per_person_csv(request, from_date, to_date, company):
    company_name = Company.objects.get(id=company)
    strfrom = datetime.datetime.strptime(from_date, "%d-%m-%Y")
    strto = datetime.datetime.strptime(to_date, "%d-%m-%Y")
    get_discount = int(re.findall('\d+', Company.objects.get(id=company).discount)[0]) * 0.01
    report = OrderItems.objects.filter(Q(order__date__range=(strfrom, strto)),
                                       Q(order__user__usercompanycard__company_id=company), Q(order__complete=True),
                                       Q(sold=True), ~Q(order__user_id=None), ~Q(order__user_id=None))
    users = report.values('order__user__username', 'order__user__last_name', 'order__user__first_name').distinct()
    sum_up = users.values('order__user__username', 'order__date').annotate(
        per_order=Sum(F('quantity') * (F('product__product__price')), output_field=DecimalField())) \
        .annotate(user_cost=Case(
        When(per_order__gt=30, then=(F('per_order') - (30 * get_discount))),
        When(per_order__lte=30, then=(F('per_order') * (1 - get_discount))),
        output_field=DecimalField(decimal_places=2))) \
        .annotate(company_cost=Case(
        When(per_order__gt=30, then=(30 * get_discount)),
        When(per_order__lte=30, then=(Sum(((F('quantity') * (F('product__product__price'))) * get_discount)))),
        output_field=DecimalField(decimal_places=2)
    ))
    response = HttpResponse(content_type='text/csv')
    filename = str(company_name.name) + '.csv'
    response['Content-Disposition'] = 'attachment; filename={}'.format(urlquote(filename))
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['shortsign', 'name', 'last name', 'personal number', 'client cost', 'comp cost', 'sum'])
    for n in users:
        writer.writerow(
            [n['order__user__username'],
             n['order__user__first_name'], n['order__user__last_name'],
             (list(map(itemgetter(0), (Personal_number.objects.filter(user_id__username=n.get('order__user__username'))
                                       .values_list('pers_number')))) or ''),
             sum_up.filter(order__user__username=n.get('order__user__username')).aggregate(
                 user_monthly=Sum('user_cost', output_field=DecimalField()))['user_monthly'],
             sum_up.filter(order__user__username=n.get('order__user__username')).aggregate(
                 company_user=Sum('company_cost', output_field=DecimalField()))['company_user'],
             sum_up.filter(order__user__username=n.get('order__user__username')).aggregate(
                 total=Sum('per_order', output_field=DecimalField()))['total']
             ])
    return response


@permission_required('canteen.draw_report')
def orders_for_the_day(request, day):
    template = loader.get_template('canteen/order_for_the_day.html')
    strday = datetime.datetime.strptime(day, "%d-%m-%Y")
    dishes = OrderItems.objects.filter(Q(order__date__exact=strday), ~Q(quantity__isnull=True), ~Q(quantity=0),
                                       Q(product__isnull=False)).distinct().values('product__product__name')
    dishes_list = dishes.distinct().annotate(quantity=Sum(F('quantity')))
    context = {'day': day, 'dishes_list': dishes_list}
    return HttpResponse(template.render(context, request))


@permission_required('canteen.draw_report')
def orders_for_the_day_csv(request, day):
    strday = datetime.datetime.strptime(day, "%d-%m-%Y")
    dishes = OrderItems.objects.filter(Q(order__date__exact=strday), ~Q(quantity__isnull=True),
                                       Q(product__isnull=False),
                                       ~Q(quantity=0)).distinct().values('product__product__name')
    dishes_list = dishes.distinct().annotate(quantity=Sum(F('quantity')))
    response = HttpResponse(content_type='text/csv')
    filename = str(strday.date()) + '.csv'
    response['Content-Disposition'] = 'attachment; filename={}'.format(urlquote(filename))
    writer = csv.writer(response, delimiter=';')
    writer.writerow(["orders for the day: ", strday.date()])
    writer.writerow(["dish", "quantity"])
    for n in dishes_list:
        writer.writerow([n.get('product__product__name'), n.get('quantity')])
    return response


@permission_required('canteen.draw_report')
def show_cancel_orders(request, from_date, to_date, user_id):
    template = loader.get_template('canteen/show_cancel_orders.html')
    cancellation_time = datetime.datetime.now()
    strfrom = datetime.datetime.strptime(from_date, "%d-%m-%Y")
    strto = datetime.datetime.strptime(to_date, "%d-%m-%Y")
    orders = OrderItems.objects.filter(Q(order__date__range=[strfrom, strto]), ~Q(product__product__name=None),
                                       Q(order__user_id=user_id), Q(order__complete=False))
    context = {'orders': orders, 'user_id': user_id, 'from_date': from_date, 'to_date': to_date,
               'cancellation_time': cancellation_time, 'strfrom': strfrom}
    return HttpResponse(template.render(context, request))


@permission_required('canteen.draw_report')
def confirm_cancel_orders(request, from_date, to_date, user_id):
    strfrom = datetime.datetime.strptime(from_date, "%d-%m-%Y")
    strto = datetime.datetime.strptime(to_date, "%d-%m-%Y")
    OrderItems.objects.filter(Q(order__date__range=[strfrom, strto]),
                              Q(order__user_id=user_id), Q(order__complete=False)).delete()
    Order.objects.filter(Q(date__range=[strfrom, strto]), Q(user_id=user_id), Q(complete=False)).delete()
    url = reverse('canteen:canteen_reports')
    return HttpResponseRedirect(url)


@permission_required('canteen.draw_report')
def incomplete_orders(request, from_date, to_date):
    template = loader.get_template('canteen/incomplete_orders.html')
    strfrom = datetime.datetime.strptime(from_date, "%d-%m-%Y")
    strto = datetime.datetime.strptime(to_date, "%d-%m-%Y")
    report = OrderItems.objects.filter(Q(order__date__range=(strfrom, strto)), Q(order__complete=False),
                                       ~Q(order__user_id=None), ~Q(order__user_id=None))
    users = report.values('order__date').distinct()
    per_person = users.distinct().annotate(
        full_price=Sum(F('quantity') * (F('product__product__price')), output_field=DecimalField()))
    calculations = per_person \
        .annotate(user_cost=Case(
        When(full_price__gt=30, then=(F('full_price') - (30 * 0.6))),
        When(full_price__lte=30, then=(F('full_price') * 0.4)),
        output_field=DecimalField(decimal_places=2))) \
        .annotate(company_cost=Case(
        When(full_price__lte=30, then=(Sum(((F('quantity') * (F('product__product__price'))) * 0.6)))),
        When(full_price__gt=30, then=(Value(30 * 0.6))),
        output_field=DecimalField(decimal_places=2))) \
        .values('order__date', 'order__user__personal_number__pers_number', 'order__user_id__username',
                'order__user__usercompanycard__company_id__name',
                'full_price', 'company_cost', 'user_cost')
    return HttpResponse(template.render({'users': users, 'report': report, 'from_date': from_date, 'to_date': to_date,
                                         'calculations': calculations}, request))


@permission_required('canteen.change_company')
def company_serialize(request):
    all_companies = Company.objects.values('id', 'name')
    json_serializer = json.dumps(list(all_companies))
    return HttpResponse(json_serializer, content_type='application/json')


@permission_required('canteen.diner_front')
def orders_serialize(request):
    all_orders = UserCompanyCard.objects.values('company__usercompanycard__card')
    json_serializer = json.dumps(list(all_orders))
    return HttpResponse(json_serializer, content_type='application/json')


def user_card_serialize(request):
    card = UserCompanyCard.objects.values('user_id', 'card')
    json_serializer = json.dumps(list(card))
    return HttpResponse(json_serializer, content_type='application/json')


def get_card(request, date):
    template = loader.get_template('canteen/get_card.html')
    denied_template = loader.get_template('canteen/access_denied.html')
    if request.method == 'POST':
        search_id = request.POST.get('textfield', None)
        try:
            card = UserCompanyCard.objects.get(card=search_id).user_id
            url = reverse('canteen:order_touch', kwargs={'date': date, 'card': card})
            return HttpResponseRedirect(url)
        except UserCompanyCard.DoesNotExist:
            return HttpResponse(denied_template.render({}, request))
    else:
        return HttpResponse(template.render({}, request))


def order_touch(request, date, card):
    template = loader.get_template('canteen/order_touch.html')
    too_late_template = loader.get_template('canteen/touch_too_late.html')
    try:
        new_order = get_object_or_404(Order, date=date, user_id=card)
    except:
        new_order = get_object_or_404(Order, date=date, user_id=None)
    orderformset = inlineformset_factory(Order, OrderItems, extra=1, fields='__all__', can_delete=True)
    ordering_user = card
    consentText = Consent.objects.get(app='Canteen')
    try:
        consentAnswer = OrderConsents.objects.get(order_id=new_order.id).answer
    except:
        consentAnswer = False
    consentForm = ConsentForm(request.POST)
    form = OrderForm(request.POST, instance=new_order)
    formset = orderformset(request.POST, instance=new_order)
    if request.method == 'POST':
        if form.is_valid():
            if formset.is_valid():
                if datetime.datetime.now() < datetime.datetime.combine(datetime.datetime.strptime(date, "%Y-%m-%d"),
                                                                       datetime.time(9, 30)):
                    try:
                        create_order = get_object_or_404(Order, date=date, user_id=ordering_user)
                        if consentForm.is_valid():
                            OrderConsents.objects.filter(Q(order_id=create_order.id), Q(consent_id=consentText.id)) \
                                .update(consent_id=consentText.id, answer=consentForm.cleaned_data['answer'])
                    except:
                        create_order = Order.objects.create(date=form.cleaned_data['date'], user_id=ordering_user)
                        if consentForm.is_valid():
                            OrderConsents.objects.create(order_id=create_order.id,
                                                         consent_id=consentText.id,
                                                         answer=consentForm.cleaned_data['answer']).save()
                    new = formset.save()
                    for n in new:
                        if n.quantity != 0:
                            n.order_id = create_order.id
                            n.sold = True
                            n.save()
                            create_order.save()
                    return HttpResponseRedirect(reverse('canteen:menu_touch'))
                else:
                    return HttpResponse(too_late_template.render({}, request))
    else:
        form = OrderForm(instance=new_order)
        formset = orderformset(instance=new_order)
        for n in formset:
            n.fields['product'].queryset = Menu.objects.filter(date=date)
    context = {'new_order': new_order, 'form': form, 'formset': formset, 'ordering_user': ordering_user, 'date': date,
               'consentForm': consentForm, 'consentText': consentText, 'consentAnswer': consentAnswer}
    return HttpResponse(template.render(context, request))


def menu_touch(request):
    template = loader.get_template('canteen/menu_touch.html')
    order_time = datetime.datetime.now()
    url = request.build_absolute_uri().rsplit('/', 1)[1]
    menu = Menu.objects.all()
    product = Product.objects.all()
    start_week = datetime.date.today() - datetime.timedelta(datetime.date.today().weekday())
    end_week = start_week + datetime.timedelta(6)
    today = datetime.date.today()
    monday = datetime.date.today() - datetime.timedelta(datetime.date.today().weekday())
    tuesday = monday + datetime.timedelta(1)
    wednesday = monday + datetime.timedelta(2)
    thursday = monday + datetime.timedelta(3)
    friday = monday + datetime.timedelta(4)
    monday_menu = Menu.objects.filter(Q(date__contains=monday))
    tuesday_menu = Menu.objects.filter(Q(date__contains=tuesday))
    wednesday_menu = Menu.objects.filter(Q(date__contains=wednesday))
    thursday_menu = Menu.objects.filter(Q(date__contains=thursday))
    friday_menu = Menu.objects.filter(Q(date__contains=friday))
    context = {'menu': menu, 'start_week': start_week, 'end_week': end_week, 'monday_menu': monday_menu,
               'tuesday_menu': tuesday_menu, 'wednesday_menu': wednesday_menu, 'thursday_menu': thursday_menu,
               'friday_menu': friday_menu, 'monday': monday, 'tuesday': tuesday, 'wednesday': wednesday,
               'thursday': thursday, 'friday': friday, 'today': today, 'product': product, 'url': url,
               'order_time': order_time}
    return HttpResponse(template.render(context, request))


def touch_next_week(request):
    template = loader.get_template('canteen/menu_touch.html')
    order_time = datetime.datetime.now()
    url = request.build_absolute_uri().rsplit('/', 1)[1]
    menu = Menu.objects.all()
    product = Product.objects.all()
    today = datetime.date.today()
    next_start = today + datetime.timedelta(days=-today.weekday(), weeks=1)
    next_end = next_start + datetime.timedelta(6)
    next_monday = next_start
    next_tuesday = next_monday + datetime.timedelta(1)
    next_wednesday = next_monday + datetime.timedelta(2)
    next_thursday = next_monday + datetime.timedelta(3)
    next_friday = next_monday + datetime.timedelta(4)
    next_monday_menu = Menu.objects.filter(Q(date__contains=next_monday))
    next_tuesday_menu = Menu.objects.filter(Q(date__contains=next_tuesday))
    next_wednesday_menu = Menu.objects.filter(Q(date__contains=next_wednesday))
    next_thursday_menu = Menu.objects.filter(Q(date__contains=next_thursday))
    next_friday_menu = Menu.objects.filter(Q(date__contains=next_friday))
    context = {'menu': menu, 'start_week': next_start, 'end_week': next_end, 'monday_menu': next_monday_menu,
               'tuesday_menu': next_tuesday_menu, 'wednesday_menu': next_wednesday_menu,
               'thursday_menu': next_thursday_menu, 'friday_menu': next_friday_menu, 'monday': next_monday,
               'tuesday': next_tuesday, 'wednesday': next_wednesday, 'thursday': next_thursday, 'friday': next_friday,
               'today': today, 'product': product, 'url': url, 'order_time': order_time}
    return HttpResponse(template.render(context, request))


def card_access_denied(request):
    return HttpResponse(loader.get_template('canteen/access_denied.html').render({}, request))


def touch_too_late(request):
    return HttpResponse(loader.get_template('canteen/touch_too_late.html').render({}, request))
