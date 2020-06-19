from django.contrib import admin
from canteen.models import Order, OrderItems, OrderConsents, Company, UserCompanyCard, Product, Menu

admin.site.register(Order)
admin.site.register(OrderItems)
admin.site.register(OrderConsents)
admin.site.register(Company)
admin.site.register(UserCompanyCard)
admin.site.register(Product)


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('date', 'product')
    search_fields = ['date', 'product__name']
