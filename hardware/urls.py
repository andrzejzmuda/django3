from os import name
from django.urls import path
from . import views

app_name = 'hardware'
urlpatterns = [
    path('', views.search_devices, name='search_devices'),
    path('add_device/', views.add_device, name='add_device'),
    path('edit_device/<int:pk>', views.edit_device, name='edit_device'),
    path('delete_device/<int:pk>', views.delete_device, name='delete_device'),
    path('assign_device_modal/<int:device_id>', views.assign_device_modal,
        name='assign_device_modal'),

    path('categories_all', views.categories_all, name='categories_all'),
    path('add_category_modal', views.add_category_modal,
        name='add_category_modal'),
    path('edit_category_modal/<int:category_id>', views.edit_category_modal,
        name='edit_category_modal'),
    path('delete_category/<int:category_id>', views.delete_category,
        name='delete_category'),

    path('events_all', views.events_all, name='events_all'),
    path('add_event_modal', views.add_event_modal,
        name='add_event_modal'),
    path('edit_event_modal/<int:event_id>', views.edit_event_modal,
        name='edit_event_modal'),
    path('delete_event/<int:event_id>', views.delete_event,
        name='delete_event'),

    path('new_owner/<int:usercard>', views.new_owner, name='new_owner'),
    path('new_user_card', views.new_user_card, name='new_user_card')
]
