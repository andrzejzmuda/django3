"""django3_apps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from dashboard import views as dashboard_views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('', dashboard_views.dashboard, name='dashboard'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('instructions/', include('instructions.urls')),
    path('canteen/', include('canteen.urls')),
    path('hr_working_hours/', include('hr_working_hours.urls')),
    path('hardware/', include('hardware.urls')),
    path('core/', include('core.urls')),
    path('dashboard/', include('dashboard.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
