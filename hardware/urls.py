from os import name
from django.urls import path
from . import views

app_name = 'hardware'
urlpatterns = [
    path('', views.search_devices, name='search_devices'),
    path('add_device/', views.add_device, name='add_device'),
    path('edit_device/<int:pk>', views.edit_device, name='edit_device'),
    path('delete_device/<int:pk>', views.delete_device, name='delete_device'),
    path('assign_device_modal/<int:device_id>', views.assign_device_modal, name='assign_device_modal'),

    path('categories_all', views.categories_all, name='categories_all'),

    path('new_owner/<int:usercard>', views.new_owner, name='new_owner'),
    path('new_user_card', views.new_user_card, name='new_user_card')
]
