from django.template import loader
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from instructions.models import Instructions
from instructions.forms import InstructionsForm
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required, login_required


@login_required()
def lista(request):
    sachnummery = Instructions.objects.order_by('-id')
    template = loader.get_template('instructions/lista.html')
    context = {'sachnummery': sachnummery}
    return HttpResponse(template.render(context, request))


@permission_required('instructions.add_instructions')
def add(request):
    template = loader.get_template('instructions/add.html')
    if request.method == 'POST':
        form = InstructionsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/instructions/')
    else:
        form = InstructionsForm()
    return HttpResponse(template.render({'form': form}, request))


@permission_required('instructions.change_instructions')
def edit(request, pk):
    edit_entry = get_object_or_404(Instructions, pk=pk)
    template = loader.get_template('instructions/edit.html')
    if request.method == 'POST':
        form = InstructionsForm(request.POST, request.FILES, instance=edit_entry)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/instructions/')
    else:
        form = InstructionsForm(instance=edit_entry)
    return HttpResponse(template.render({'form': form, 'edit_entry': edit_entry}, request))


@permission_required('instructions.delete_instructions')
def delete(request, pk):
    delfile = Instructions.objects.get(pk=pk).delete()
    if request.method == 'POST':
        form = InstructionsForm(request.POST, request.FILES, instance=delfile)
        form.u.delete()
        form.save()
    return HttpResponseRedirect('/instructions/')
