from django.contrib import admin
from hr_working_hours.models import HolidayTypes, LastDay, LocationToManager, ManagerToWorker, WorkersToLocation,\
    WorkingHours

admin.site.register(HolidayTypes)
admin.site.register(LastDay)
admin.site.register(ManagerToWorker)
admin.site.register(WorkersToLocation)


@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ('shortsign', 'card', 'entry_time', 'leaving_time')
    search_fields = ['shortsign', 'entry_time', 'leaving_time']


@admin.register(LocationToManager)
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ('get_location', 'get_detailed_location', 'manager')
    search_fields = ['location__location', 'location__detailed_location', 'manager__username']
