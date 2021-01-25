from django.urls import path

from . import views

app_name = 'instructions'
urlpatterns = [
    path('', views.lista, name='lista'),
    path('lista', views.lista, name='lista'),
    path('add/', views.add, name='add'),
    path('edit/<int:pk>', views.edit, name='edit'),
    path('delete/<int:pk>', views.delete, name='delete')
]
