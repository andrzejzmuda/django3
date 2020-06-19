from django.apps import AppConfig


class HrWorkingHoursConfig(AppConfig):
    name = 'hr_working_hours'

    def ready(self):
        self.get_model('__all__')
