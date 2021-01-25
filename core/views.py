import json
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.forms.models import modelformset_factory
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import HttpResponseRedirect, reverse
from django.db.models import Q
from django.template import loader

from core.forms import SachnrForm, DisponentForm, UploadFileForm, DispoForm
from core.models import Sachnr, Disponent, Dispo, Deliverer, Supplier


@login_required()
def main(request):
    if request.user.username == 'admin':
        dispo = Dispo.objects.all()
    elif request.user.groups.filter(name__contains='magazyn'):
        find_logistyka = Group.objects.get(name='logistyka').id
        dispo = Dispo.objects.filter(Q(disponent__shortsign__groups=find_logistyka))
    else:
        user_group = request.user.groups.all().values('id')
        dispo = Dispo.objects.filter(Q(disponent__shortsign__groups=user_group))
    if request.method == 'GET':
        form = SachnrForm()
    elif request.method == 'POST':
        form = SachnrForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            form = SachnrForm()
    template = loader.get_template('sachnr/show_all.html')
    return HttpResponse(template.render({'form': form, 'dispo': dispo}, request))


@permission_required('core.add_sachnr')
def sachnr_select_detailed_view(request):
    template = loader.get_template('sachnr/sachnr_detailed_view.html')
    return HttpResponse(template.render({}, request))


@permission_required('core.add_sachnr')
def sachnr_details(request, pk):
    sachnr_details = Sachnr.objects.filter(sachnr=pk)
    template = loader.get_template('sachnr/sachnr_details.html')
    context = {'sachnr_details': sachnr_details}
    return HttpResponse(template.render(context, request))


@permission_required('core.add_sachnr')
def edit_sachnr(request, sachnr):
    edit = Sachnr.objects.get(sachnr=sachnr)
    sachnr_disponent = Disponent.objects.filter(dispo=edit.dispo_id)
    dispo = Dispo.objects.all()
    template = loader.get_template('sachnr/edit.html')
    if request.method == 'POST':
        form = SachnrForm(request.POST, instance=edit)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('core:sachnr_select_detailed_view'))
    else:
        form = SachnrForm(instance=edit)

        return HttpResponse(template.render({'form': form, 'edit': edit, 'dispo': dispo,
                                             'sachnr_disponent': sachnr_disponent}, request))


@permission_required('core.add_sachnr')
def delete_sachnr(request, pk):
    delete = Sachnr.objects.get(id=pk).delete()
    if request.method == 'POST':
        form = SachnrForm(request.POST, instance=delete)
        form.u.delete()
        form.save()
    return HttpResponseRedirect(reverse('core:sachnr_select_detailed_view'))


@permission_required('core.can_search_for_sachnr')
def serialize_sachnr(request):
    all_sachnr = Sachnr.objects.values('id', 'sachnr', 'description')
    json_serializer = json.dumps(list(all_sachnr))
    return HttpResponse(json_serializer, content_type='application/json')


@permission_required('core.add_sachnr')
def import_data(request):
    template = loader.get_template('sachnr/import.html')
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            request.FILES['file'].save_to_database(
                model=Sachnr,
                mapdict=['sachnr', 'description', 'dispo_id'])

            return HttpResponse("OK")
        else:
            return HttpResponseBadRequest("error :(")
    else:
        form = UploadFileForm()
        return HttpResponse(template.render({'form': form}, request))


# DISPONENT #
@permission_required('core.add_disponent')
def disponent_all(request):
    find_logistyka = Group.objects.get(name='logistyka').id
    users = User.objects.filter(groups=find_logistyka)
    print(users)
    dispo_users = Disponent.objects.all()
    dispo = Dispo.objects.all()
    diff = []
    template = loader.get_template('sachnr/disponent_all.html')
    for all in users:
        found = False
        for sub in dispo_users:
            if sub.shortsign_id == all.id:
                found = True
                break
        if not found:
            diff.append(all)
    if request.method == 'POST':
        form = DisponentForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('core:disponent_all'))
    else:
        form = DisponentForm()
    return HttpResponse(template.render({'all': dispo_users, 'form': form, 'users': diff,
                                         'dispo': dispo}, request))


@permission_required('core.add_disponent')
def delete_disponent(request, pk):
    delete = Disponent.objects.get(id=pk).delete()
    if request.method == 'POST':
        form = SachnrForm(request.POST, instance=delete)
        form.u.delete()
        form.save()
    return HttpResponseRedirect(reverse('core:disponent_all'))


@permission_required('core.add_disponent')
def edit_disponent(request, pk):
    edit = Disponent.objects.filter(id=pk)
    dispo_selected = Dispo.objects.filter(disponent__id=pk)
    dispo_all = Dispo.objects.all()
    disponent_sachnr = Sachnr.objects.filter(dispo__disponent=pk)
    EditFormSet = modelformset_factory(Disponent, fields=('dispo',), max_num=1, min_num=0)
    template = loader.get_template('sachnr/edit_disponent.html')
    if request.method == 'POST':
        formset = EditFormSet(request.POST, queryset=Disponent.objects.filter(id=pk))
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(reverse('core:disponent_all'))
    else:
        formset = EditFormSet(queryset=Disponent.objects.filter(id=pk))

    return HttpResponse(template.render({'id': pk, 'form': formset, 'edit': edit,
                                         'dispo_selected': dispo_selected, 'dispo_all': dispo_all,
                                         'disponent_sachnr': disponent_sachnr}, request))

# DISPO #
@permission_required('core.add_dispo')
def dispo_all(request):
    dispo_all = Dispo.objects.all()
    template = loader.get_template('sachnr/dispo_all.html')
    if request.method == 'GET':
        form = DispoForm()
    elif request.method == 'POST':
        form = DispoForm(request.POST)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse('core:dispo_all'))
    else:
        form = DispoForm()
    return HttpResponse(template.render({'dispo_all': dispo_all, 'form': form}, request))


@permission_required('core.add_dispo')
def edit_dispo(request, pk):
    dispo_edit = Dispo.objects.get(id=pk)
    template = loader.get_template('sachnr/edit_dispo.html')
    if request.method == 'POST':
        form = DispoForm(request.POST, instance=dispo_edit)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('core:dispo_all'))
    else:
        form = SachnrForm(instance=dispo_edit)
        return HttpResponse(template.render({'form': form, 'dispo_edit': dispo_edit}, request))


@permission_required('core.add_dispo')
def dispo_delete(request, pk):
    dispo_delete = Dispo.objects.get(id=pk).delete()
    if request.method == 'POST':
        form = DispoForm(request.POST, instance=dispo_delete)
        form.u.delete()
        form.save()
    return HttpResponseRedirect(reverse('core:dispo_all'))


def serialize_deliverer(request):
    all_deliverers = Deliverer.objects.values('id', 'number', 'name')
    json_serializer = json.dumps(list(all_deliverers))
    return HttpResponse(json_serializer, content_type='application/json')


def serialize_supplier(request):
    all_suppliers = Supplier.objects.values('id', 'name')
    json_serializer = json.dumps(list(all_suppliers))
    return HttpResponse(json_serializer, content_type='application/json')
