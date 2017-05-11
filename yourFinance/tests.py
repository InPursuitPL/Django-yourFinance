from django.test import TestCase
from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from .models import Stash

class LoginTestCase(TestCase):
    """Tests for login and view profile functionalities."""
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('john',
                                             'lennon@thebeatles.com',
                                             'johnpassword')

    def test_login(self):
        self.client.login(username='john', password='johnpassword')
        response = self.client.get(reverse('view profile'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['stashNamesList'],
                         ['Bank account', 'Savings', 'Wallet', 'Others'])
        self.assertEqual(response.context['costNamesList'],
                         ['Rent and other charges', 'Transportation',
                                         'Clothes', 'Food', 'Hobby', 'Others'])


class ViewDataTestCase(TestCase):
    """Tests for view data functionality."""
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('john',
                                             'lennon@thebeatles.com',
                                             'johnpassword')
        self.client.login(username='john', password='johnpassword')

    def test_view_all_data_when_empty(self):
        response = self.client.post('/view_data/', {'startDate': '', 'endDate': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context['stashes']), '<QuerySet []>')

    def test_view_all_data(self):
        Stash.objects.create(user= self.user, name= 'Bank account',
                             date= '2001-01-01', amount= 1500)
        response = self.client.post('/view_data/', {'startDate': '', 'endDate': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context['stashes']),
                         '<QuerySet [<Stash: Bank account 2001-01-01 1500.00>]>')


class AnalyzeDataTestCase(TestCase):
    """Tests for analyze data functionality."""
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('john',
                                             'lennon@thebeatles.com',
                                             'johnpassword')
        self.client.login(username='john', password='johnpassword')

    def test_analyze_data_when_empty(self):
        response = self.client.get('/9999-12-31/analyze_record/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['templateText'],
                         'No data to analyze!')

    def test_analyze_data(self):
        Stash.objects.create(user=self.user, name='Bank account',
                             date='2001-01-01', amount=1500)
        response = self.client.get('/9999-12-31/analyze_record/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['totalAmount'],
                         1500)