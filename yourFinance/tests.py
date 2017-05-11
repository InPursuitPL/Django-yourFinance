from django.test import TestCase
from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from .models import Stash

class LoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('john',
                                             'lennon@thebeatles.com',
                                             'johnpassword')

    def testLogin(self):
        self.client.login(username='john', password='johnpassword')
        response = self.client.get(reverse('view profile'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['stashNamesList'],
                         ['Bank account', 'Savings', 'Wallet', 'Others'])


