from django.test import TestCase, Client
from dotenv import load_dotenv, dotenv_values
import random
import logging
from django.contrib.auth.models import User

load_dotenv()
config = dotenv_values(".env")


logger = logging.getLogger(__name__)

logging.basicConfig(
    filename='logfile',
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG
    )

class EditWorkerTest(TestCase):
    def test_edit(self):
        ids = []
        for n in User.objects.all().values('id'):
            ids.append(n['id'])
        client = Client()
        client.login(username='admin',password=config['passwd'])
        response = client.get('/canteen/user_companies_edit/{}'.format(random.randrange(ids)))
        self.assertEqual(response.status_code, 302)
        logger.info(f"testing edit worker module {response}")
