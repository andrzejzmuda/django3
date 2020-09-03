from django.test import TestCase, Client
import random
import logging
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

logging.basicConfig(
    filename='logfile',
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG
    )


def LoginViewTest(TestCase):
    def test_login_view(self):
        client = Client()
        response = client.get('/accounts/login/')
        self.assertEqual(reponse.status_code, 200)

    def test_user_login(self):
        client = Client()
        reponse = client.post('/accounts/login/', {'username': 'admin', 'password': '<<your_passwd>>'})
        self.assertEqual(reponse.status_code, 200)