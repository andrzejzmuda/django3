from django.contrib import admin
from .models import (Category,
                    Department,
                    Events,
                    Owner,
                    Device,
                    History)

admin.site.register(Category)
admin.site.register(Department)
admin.site.register(Events)
admin.site.register(Owner)
admin.site.register(Device)
admin.site.register(History)
