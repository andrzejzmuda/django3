from django import template
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import get_object_or_404, reverse
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import (permission_required,
                                            login_required)

from .models import (
    Category,
    Department,
    Events,
    Owner,
    Device,
    History
    )
from canteen.models import UserCompanyCard
from .forms import (
    AssignOwnerForm,
    DeviceForm,
    DeviceFormSet,
    CategoryForm,
    OwnerForm,
    SearchForm,
    NewCardForm,
    )


@login_required()
def search_devices(request):
    """
    Display your search results :model:`hardware.Device`.

    **Context**

    ``search_devices``
        A list of :model:`hardware.Device`.
    """
    template = loader.get_template('list_devices.html')
    searchForm = SearchForm()
    criteria = {}
    if request.method == "POST":
        criteria['hostname'] = request.POST['hostname']
        criteria['description'] = request.POST['description']
        criteria['history__owner__kzz__username'] = request.POST['owner']
        criteria['category__name'] = str(request.POST['category']).rstrip()
        criteria['serial_number'] = request.POST['serial_number']
        criteria['mac_address'] = request.POST['mac_address']
        criteria['history__event__action'] = request.POST['event']
        query = Device.objects.all()
        filters = search_criteria(criteria)
        print(filters)
        if criteria.items():
            query = query.filter(filters).distinct()
        else:
            query = []
        return HttpResponse(template.render(
            {
            'searched': criteria, 'query':query,
            'searchForm': searchForm
            }, request))
    else:
        return HttpResponse(template.render({'searchForm': searchForm}, request))


def search_criteria(criteria):
    """
    Searching mechanism used by :view:`hardware.search_devices`

    **Context**

    ``search_criteria``
        Searching mechanism used by :view:`hardware.views.search_devices`
    """
    filters = Q()
    if isinstance(criteria, dict):
        # if criteria['history__event__action'] != '':
        {filters.add(Q(**{k+'__icontains': v}), Q.AND) for k,v in criteria.items() if v != ''}
        # filters = Q(**{k + '__icontains': v for k, v in criteria.items()})
    else:
        filters = Q()
    return filters


@permission_required('hardware.add_device')
def add_device(request):
    """
    Creates a new device with a new history.

    **Context**
    Creates a new instance of :model:`hardware.Device`
    """
    template = loader.get_template('device.html')
    next = request.POST.get('next', 'hardware:search_devices')
    form = DeviceForm(request.POST)
    formset = DeviceFormSet(request.POST, request.FILES)
    if request.method == 'POST':
        if form.is_valid():
            new_device = form.save()
            new_history = DeviceFormSet(request.POST, request.FILES, instance=new_device)
            if new_history.is_valid():
                new_device.save()
                new_history.save()
                return HttpResponseRedirect(reverse(next))
    else:
        form = DeviceForm()
        formset = DeviceFormSet(instance=Device())
    return HttpResponse(template.render({'form': form, 'formset': formset}, request))


@permission_required('hardware.change_device')
def edit_device(request, pk):
    """
    Display an individual :model:`hardware.Device`.

    **Context**

    ``edit_device``
        An instance of :model:`hardware.Device`.
    """
    template = loader.get_template('device.html')
    next = request.POST.get('next', 'hardware:search_devices')
    device = get_object_or_404(Device, pk=pk)
    if request.method == 'POST':
        form = DeviceForm(request.POST, instance=device)
        formset = DeviceFormSet(request.POST, request.FILES, instance=device)
        if form.is_valid() and formset.is_valid():
                form.save()
                formset.save()
                return HttpResponseRedirect(reverse(next))
    else:
        form = DeviceForm(instance=device)
        formset = DeviceFormSet(instance=device)
    return HttpResponse(template.render({
        'form': form, 'formset': formset, 'device': device},
        request))


@permission_required('hardware.delete_device')
def delete_device(request, pk):
    """
    Deletes an individual :model:`hardware.Device` instance

    **Context**

    ``delete_device``
        An instance of :model:`hardware.Device`.
    """
    next = request.POST.get('next', 'hardware:search_devices')
    try:
        device = Device.objects.get(id=pk).delete()
        if request.method == 'POST':
            form = DeviceForm(request.POST, instance=device)
            form.u.delete()
            form.save()
    except ObjectDoesNotExist:
        print(("No device with id {0}").format(pk))
    finally:
        return HttpResponseRedirect(reverse(next))


@permission_required('hardware.edit_owner')
def assign_device_modal(request, device_id):
    """
    Shows a modal window to assign a device to a user

    **Context**

    ``assign_device_modal``
        The window containing a form used to assign a device to a user.
        The view utilises :view:`hardware.views.assign_device`
    """
    template = loader.get_template('assign_device_modal.html')
    next = request.POST.get('next', 'hardware:edit_device')
    form = AssignOwnerForm(request.POST, initial={'device': device_id})
    if request.method == 'POST':
        assign_device(request.POST['device'], request.POST['card'])
        return HttpResponseRedirect(reverse(next, args=[device_id]))
    else:
        form = AssignOwnerForm(initial={'device': device_id})
    return HttpResponse(template.render(
        {'form': form, 'device': device_id}, request))


def assign_device(device_id, usercard):
    """
    Assigns a device to a user

    **Context**
    ``assign_device``

        A method assigning a device to a user.
        Models used:
        :model:`canteen.models.UserCompanyCard`,
        :models:`hardware.models.Owner`
    """
    event, obj = Events.objects.get_or_create(action='new owner')
    card = UserCompanyCard.objects.get(card_original=usercard) #TODO: redirect if no card and user
    owner, created = Owner.objects.get_or_create(kzz_id=card.user_id)
    new = History(
        device_id=device_id,
        event_id=event.id,
        owner_id = owner.id
        )
    new.save()
    return new


@permission_required('hardware.edit_owner')
def new_user_card(request):
    template = loader.get_template('new_user_card.html')
    form = NewCardForm()
    new_user = {}
    if request.method == 'POST':
        new_user['user'] = request.POST['user']
        new_user['card'] = request.POST['card']
        user, created = User.objects.update_or_create(
            username=new_user['user'],
            defaults={
                'password': get_random_string(length=32)
                }
            )
        UserCompanyCard.objects.filter(~Q(user_id=user.id), Q(card_original=new_user['card'])).delete()
        card, created = UserCompanyCard.objects.update_or_create(
            user_id=user.id,
            defaults={
                'user_id':user.id,
                'card_original': new_user['card']
            }
        )
    else:
        form = NewCardForm()
    return HttpResponse(template.render({'form': form}, request))


@permission_required('hardware.edit_owner')
def new_owner(request):
    template = loader.get_template('owner.html')
    if request.method == ' POST':
        form = OwnerForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = OwnerForm()
    return HttpResponse(template.render({'form': form}, request))


@permission_required('hardware.edit_category')
def categories_all(request):
    template = loader.get_template('categories_all.html')
    categories = Category.objects.all()
    return HttpResponse(template.render({'categories': categories}, request))


@permission_required('hardware.edit_category')
def edit_category_modal(request, category_id):
    """
    Edits a category name

    **Context**

    ``edit_category_modal``
        The window, which allows editing a modal name.
    """
    category_edit = Category.objects.get(id=category_id)
    template = loader.get_template('edit_category_modal.html')
    next = request.POST.get('next', 'hardware:categories_all')
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category_edit)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(next))
    else:
        form = CategoryForm(instance=category_edit)
    return HttpResponse(
        template.render({'form': form, 'category_edit': category_edit,
        'category_id': category_id}, request))

@permission_required('hardware.delete_category')
def delete_category(request, category_id):
    """
    Deletes a category

    **Context**
    ``delete_category``
        Function available in :view:`hardware.views.edit_category_modal`
    """
    category_delete = Category.objects.get(id=category_id)
    next = request.POST.get('next', 'hardware:categories_all')
    try:
        category = Category.objects.get(id=category_id).delete()
        if request.method == 'POST':
            form = CategoryForm(request.POST, instance=category_delete)
            form.u.delete()
            form.save()
    except ObjectDoesNotExist:
        print(("No such category: {0}").format(category_delete.name))
    finally:
        return HttpResponseRedirect(reverse(next))