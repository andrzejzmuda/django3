from django.test import TestCase
import string
import random

from models import Category, History


class CategoryTest(TestCase):
    def setUp(self):
        self.length = [random.randrange(1,100,1) for i in range(10)]
        self.names = list(map(
            lambda x: ''.join(random.choice(string.ascii_letters)
            for i in range(x)), self.length))
        list(map(lambda n: Category.objects.create(name=n), self.names))
        # Category.objects.create(name='test1')
        # Category.objects.create(name='1234')

    def test_instance(self):
        # w = self.create_records()
        # test1 = Category.objects.get(name='test1')
        # test2 = Category.objects.get(name='1234')
        names = self.names
        for n in names:
            n = Category.objects.get(name=n)
            self.assertTrue(isinstance(n, Category)),
            self.assertEqual(n.__str__(), (n.name))
