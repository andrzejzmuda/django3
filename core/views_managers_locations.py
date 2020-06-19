# -*- coding: utf-8 -*-
from core.forms_managers_locations import LocationForm, ResponsibleForm
from core.models_managers_locations import Location, Responsibles
from django.shortcuts import reverse
from django.forms.models import modelformset_factory
from django.contrib.auth.models import User
from django.contrib.auth.decorators import permission_required
from django.shortcuts import HttpResponseRedirect
from django.template import loader
from django.http import HttpResponse


# MANAGER #
@permission_required('core.add_location')
def responsible_all(request):
    managers = User.objects.filter(groups__name__icontains='managers')
    responsibles = Responsibles.objects.all()
    locations = Location.objects.all()
    diff = []
    template = loader.get_template('managers_locations/responsible_all.html')
    for all in locations:
        found = False
        for sub in responsibles:
            if sub.location_id == all.id:
                found = True
                break
        if not found:
            diff.append(all)
    if request.method == 'POST':
        form = ResponsibleForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('core:responsible_all'))
    else:
        form = ResponsibleForm()
    return HttpResponse(template.render({'all': responsibles, 'form': form, 'users': managers, 'locations': diff},
                                        request))


@permission_required('core.add_location')
def delete_responsible(request, pk):
    delete = Responsibles.objects.get(id=pk).delete()
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=delete)
        form.u.delete()
        form.save()
    return HttpResponseRedirect(reverse('core:responsible_all'))


@permission_required('core.add_location')
def edit_responsible(request, pk):
    edit = Responsibles.objects.filter(id=pk)
    responsibles_selected = User.objects.filter(responsibles__id=pk)
    managers = User.objects.filter(groups__name__icontains='managers')
    EditFormSet = modelformset_factory(Responsibles, fields=('shortsign',), max_num=1, min_num=0)
    template = loader.get_template('managers_locations/edit_responsible.html')
    if request.method == 'POST':
        formset = EditFormSet(request.POST, queryset=Responsibles.objects.filter(id=pk))
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(reverse('core:responsible_all'))
    else:
        formset = EditFormSet(queryset=Responsibles.objects.filter(id=pk))

    return HttpResponse(template.render({'id': pk, 'form': formset, 'edit': edit,
                                         'responsibles_selected': responsibles_selected, 'location_all': location_all,
                                         'managers': managers}, request))

# LOCATION #
@permission_required('core.add_location')
def location_all(request):
    location_all = Location.objects.all()
    template = loader.get_template('managers_locations/location_all.html')
    if request.method == 'GET':
        form = LocationForm()
    elif request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse('core:location_all'))
    else:
        form = LocationForm()
    return HttpResponse(template.render({'location_all': location_all, 'form': form}, request))


@permission_required('core.add_location')
def edit_location(request, pk):
    location_edit = Location.objects.get(id=pk)
    template = loader.get_template('managers_locations/edit_location.html')
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=location_edit)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('core:location_all'))
    else:
        form = ResponsibleForm(instance=location_edit)

        return HttpResponse(template.render({'form': form, 'location_edit':location_edit}, request))


@permission_required('core.add_location')
def location_delete(request, pk):
    location_delete = Location.objects.get(id=pk).delete()
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=location_delete)
        form.u.delete()
        form.save()
    return HttpResponseRedirect(reverse('core:location_all'))
