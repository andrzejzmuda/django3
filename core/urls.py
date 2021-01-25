from django.urls import path

from . import views, views_managers_locations, views_users_addons

app_name = 'core'
urlpatterns = [
    path('', views.main, name='main'),
    path('main', views.main, name='main'),
    path('edit_sachnr/<str:sachnr>', views.edit_sachnr, name='edit_sachnr'),
    path('delete_sachnr/<int:pk>', views.delete_sachnr, name='delete_sachnr'),
    path('disponent_all/', views.disponent_all, name='disponent_all'),
    path('edit_disponent/<int:pk>', views.edit_disponent, name='edit_disponent'),
    path('delete_disponent/<int:pk>', views.delete_disponent, name='delete_disponent'),
    path('serialize_sachnr/', views.serialize_sachnr, name='serialize_sachnr'),
    path('sachnr_detailed_view/', views.sachnr_select_detailed_view, name='sachnr_select_detailed_view'),
    path('sachnr_details/<int:pk>', views.sachnr_details, name='sachnr_details'),
    path('import', views.import_data, name='import_data'),
    path('dispo_all', views.dispo_all, name='dispo_all'),
    path('dispo_delete/<int:pk>', views.dispo_delete, name='dispo_delete'),
    path('edit_dispo/<int:pk>', views.edit_dispo, name='edit_dispo'),
    path('serialize_deliverer/', views.serialize_deliverer, name='serialize_deleverer'),
    # managers_locations
    path('edit_responsible/<int:pk>', views_managers_locations.edit_responsible, name='edit_responsible'),
    path('responsible_all', views_managers_locations.responsible_all, name='responsible_all'),
    path('delete_responsible/<int:pk>', views_managers_locations.delete_responsible, name='delete_responsible'),
    path('location_all', views_managers_locations.location_all, name='location_all'),
    path('location_delete/<int:pk>', views_managers_locations.location_delete, name='location_delete'),
    path('edit_location/<int:pk>', views_managers_locations.edit_location, name='edit_location'),
    # users_addons
    path('pers_numbers', views_users_addons.pers_numbers, name='pers_numbers'),
    path('edit_pers_number/<int:pk>', views_users_addons.edit_pers_number, name='edit_pers_numbers'),
    path('delete_pers_number/<int:pk>', views_users_addons.delete_pers_number, name='delete_pers_number'),
    path('users_serialize', views_users_addons.users_serialize, name='users_serialize'),
    path('users_temp_serialize', views_users_addons.users_temp_serialize, name='users_temp_serialize'),
    path('NewUserS1', views_users_addons.NewUserS1, name='NewUserS1'),
    path('NewUserS2/<str:shortsign>', views_users_addons.NewUserS2, name='NewUserS2'),
    path('NewUserS3/<str:shortsign>', views_users_addons.NewUserS3, name='NewUserS3'),
    path('NewAccount/<str:shortsign>/<str:manager>', views_users_addons.NewAccount, name='NewAccount'),
    path('AddCompany/<str:shortsign>/<str:operator>', views_users_addons.AddCompany, name='AddCompany'),
    path('AddPersNumber/<str:shortsign>/<str:pers_number>', views_users_addons.AddPersNumber,
         name='AddPersNumber'),
    path('SaveCard/<str:shortsign>/<str:card>', views_users_addons.SaveCard, name='SaveCard'),
    path('PrintCard/<str:shortsign>', views_users_addons.PrintCard, name='PrintCard'),
    path(
        'SetLastDay/<str:shortsign>/<last_day>/<first_day>', views_users_addons.SetLastDay, name='SetLastDay'),
    # suppliers
    path('serialize_supplier', views.serialize_supplier, name='serialize_supplier'),
]
