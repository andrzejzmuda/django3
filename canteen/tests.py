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

# class EditWorkerTest(TestCase):
    # def test_edit(self):
    #     client = Client()
    #     client.post('/accounts/login/', {'username': 'admin', 'password':''})
    #     # response = client.get('/canteen/user_companies_edit/{}'.format(random.randrange(0,User.objects.all().count())))
    #     response = client.get('/canteen/user_companies_edit/11')
    #     result = self.assertEqual(response.status_code, 200)
    #     logger.info(f"testing edit worker module {result}")
    # def test_hr_reports(self):
