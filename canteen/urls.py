from django.urls import path

from . import views

app_name = 'canteen'
urlpatterns = [
   path('', views.menu_all, name='menu_all'),
   path('menu_all', views.menu_all, name='menu_all'),
   path('next_week_menu', views.next_week_menu, name='next_week_menu'),
   path('users_admin', views.users_admin, name='users_admin'),
   path('companies', views.companies, name='companies'),
   path('company_serialize', views.company_serialize, name='company_serialize'),
   path('orders_serialize', views.orders_serialize, name='orders_serialize'),
   path('company_edit/<int:pk>', views.company_edit, name='company_edit'),
   path('company_delete/<int:pk>', views.company_delete, name='company_delete'),
   path('users_company', views.users_company, name='users_company'),
   path('user_companies_edit/<int:pk>', views.user_companies_edit, name='user_companies_edit'),
   path('deactivate_user/<int:pk>', views.deactivate_user, name='deactivate_user'),
   path('activate_user/<int:pk>', views.activate_user, name='activate_user'),
   path('user_delete/<int:pk>', views.user_delete, name='user_delete'),
   path('menu_delete/<int:pk>', views.menu_delete, name='menu_delete'),
   path('dishes_all', views.dishes_all, name='dishes_all'),
   path('order/(<date>[0-9]{4}-[0-9]{2}-[0-9]{2})', views.order, name='order'),
   path('dishes_delete/<int:pk>', views.dishes_delete, name='dishes_delete'),
   path('dishes_edit/<int:pk>', views.dishes_edit, name='dishes_edit'),
   path('canteen_reports', views.reports, name='canteen_reports'),
   path('report_per_company/<from_date>[0-9]{2}-[0-9]{2}-[0-9]{4}/<to_date>[0-9]{2}-[0-9]{2}-[0-9]{4}/'
        '<int:company>', views.report_per_company, name='report_per_company'),
   path('report_from_to_csv/<from_date>[0-9]{2}-[0-9]{2}-[0-9]{4}/<to_date>[0-9]{2}-[0-9]{2}-[0-9]{4}/'
        '<int:company>', views.report_per_company_csv, name='report_from_to_csv'),
   path('report_per_person/<from_date>[0-9]{2}-[0-9]{2}-[0-9]{4}/<to_date>[0-9]{2}-[0-9]{2}-[0-9]{4}/'
        '<int:company>', views.report_per_person, name='report_per_person'),
   path('report_per_person_csv/<from_date>[0-9]{2}-[0-9]{2}-[0-9]{4}/<to_date>[0-9]{2}-[0-9]{2}-[0-9]{4}/'
        '<int:company>', views.report_per_person_csv, name='report_per_person_csv'),
   path('incomplete_orders/<from_date>[0-9]{2}-[0-9]{2}-[0-9]{4}/<to_date>[0-9]{2}-[0-9]{2}-[0-9]{4}',
        views.incomplete_orders, name='incomplete_orders'),
   path('show_cancel_orders/<from_date>[0-9]{2}-[0-9]{2}-[0-9]{4}/<to_date>[0-9]{2}-[0-9]{2}-[0-9]{4}/'
        '<int:user_id>', views.show_cancel_orders, name='show_cancel_orders'),
   path('confirm_cancel_orders/<from_date>[0-9]{2}-[0-9]{2}-[0-9]{4}/<to_date>[0-9]{2}-[0-9]{2}-[0-9]{4}/'
        '<int:user_id>', views.confirm_cancel_orders, name='confirm_cancel_orders'),
   path('orders_for_the_day/<day>[0-9]{2}-[0-9]{2}-[0-9]{4}', views.orders_for_the_day, name='orders_for_the_day'),
   path('orders_for_the_day_csv/<day>[0-9]{2}-[0-9]{2}-[0-9]{4}', views.orders_for_the_day_csv,
        name='orders_for_the_day_csv'),
   path('my_account', views.my_account, name='my_account'),
   path('diner_front', views.diner_front, name='diner_front'),
   path('how_many_left', views.how_many_left, name='how_many_left'),
   path('show_order/<int:card>', views.show_order, name='show_order'),
   path('close_order/<int:card>', views.close_order, name='close_order'),
   path('sold_unsold/<int:pk>', views.sold_unsold, name='sold_unsold'),
   path('change_quantity/<int:pk>/<operator>[\w-]+', views.change_quantity,
        name='change_quantity'),
   path('user_card_serialize', views.user_card_serialize, name='user_card_serialize'),
   path('get_card/<date>[0-9]{4}-[0-9]{2}-[0-9]{2}', views.get_card, name='get_card'),
   path('order_touch/<date>[0-9]{4}-[0-9]{2}-[0-9]{2}/<int:card>', views.order_touch, name='order_touch'),
   path('menu_touch', views.menu_touch, name='menu_touch'),
   path('touch_next_week', views.touch_next_week, name='touch_next_week'),
   path('touch_too_late', views.touch_too_late, name='touch_too_late')
]
