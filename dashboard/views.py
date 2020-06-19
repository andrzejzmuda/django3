from django.template import RequestContext
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


@login_required()
def dashboard(request):
    template = loader.get_template('dashboard/dashboard.html')
    return HttpResponse(template.render({}, request))
