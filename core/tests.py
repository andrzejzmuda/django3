from django.test import TestCase, Client
from django.urls import reverse
from core.forms import SachnrForm
from core.models import Sachnr, Dispo


class TestModels(TestCase):

    def create_dispo(self, name='dispoł1', ekg='lpt'):
        return Dispo.objects.create(name=name, ekg=ekg)

    def create_sachnr(self, sachnr='1234', description='description', dispo_id=1):
        return Sachnr.objects.create(sachnr=sachnr, description=description, dispo_id=dispo_id)

    def test_creation(self):
        w = self.create_dispo()
        x = self.create_sachnr()
        self.assertTrue(isinstance(w, Dispo))
        self.assertEqual(w.__str__(), (w.name, w.ekg))
        self.assertTrue(isinstance(x, Sachnr))
        self.assertEqual(x.__str__(), (x.sachnr, x.description, (x.dispo.name, x.dispo.ekg)))

