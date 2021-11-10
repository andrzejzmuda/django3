from django.contrib.auth.models import User
from hardware.models import UserCompanyCard


class CustomRouting:
    def db_for_write(self, model, **hints):
        if model == UserCompanyCard:
            raise Exception("This model is read only!")
        return None
