from django.test import TestCase
from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from .models import Stash

class LoginTestCase(TestCase):
    """Tests for login and view profile functionalities."""
    def setUp(self):
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
        self.user = User.objects.create_user('john',
                                             'lennon@thebeatles.com',
                                             'johnpassword')
        self.client.login(username='john', password='johnpassword')

    def test_view_all_data_when_empty(self):
        response = self.client.post('/view_data/', {'startDate': '', 'endDate': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['stashes_groups_and_totals'], [])

    def test_view_all_data(self):
        Stash.objects.create(user= self.user, name= 'Bank account',
                             date= '2001-01-01', amount= 1500)
        response = self.client.post('/view_data/', {'startDate': '', 'endDate': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context['stashes_groups_and_totals'][0][0]),
                         '[<Stash: Bank account 2001-01-01 1500.00>]')


class DeleteDataTestCase(TestCase):
    """Tests for delete data functionality."""
    def setUp(self):
        self.user = User.objects.create_user('john',
                                             'lennon@thebeatles.com',
                                             'johnpassword')
        self.client.login(username='john', password='johnpassword')

    def test_delete_data(self):
        # Creates two stash objects for different dates.
        Stash.objects.create(user=self.user, name='Bank account',
                             date='2001-01-01', amount=1800)
        Stash.objects.create(user=self.user, name='Bank account',
                             date='2002-02-02', amount=2500)
        # Asserts two objects are visible in view data.
        response = self.client.post('/view_data/', {'startDate': '', 'endDate': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['stashes_groups_and_totals']), 2)
        self.assertEqual(str(response.context['stashes_groups_and_totals'][0][0]),
                         '[<Stash: Bank account 2001-01-01 1800.00>]')
        self.assertEqual(str(response.context['stashes_groups_and_totals'][1][0]),
                         '[<Stash: Bank account 2002-02-02 2500.00>]')
        # Deletes one of stash objects.
        response = self.client.post('/delete_multiple_data/',
                                    {'startDate': '2002-02-02', 'endDate': '2002-02-02'})
        self.assertEqual(response.status_code, 200)
        # Asserts only one object is left in view data.
        response = self.client.post('/view_data/', {'startDate': '', 'endDate': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['stashes_groups_and_totals']), 1)
        self.assertEqual(str(response.context['stashes_groups_and_totals'][0][0]),
                         '[<Stash: Bank account 2001-01-01 1800.00>]')


class AnalyzeDataTestCase(TestCase):
    """Tests for analyze data functionality."""
    def setUp(self):
        self.user = User.objects.create_user('john',
                                             'lennon@thebeatles.com',
                                             'johnpassword')
        self.client.login(username='john', password='johnpassword')

    def test_analyze_data_when_empty(self):
        response = self.client.get('/9999-12-31/analyze_record/')
        self.assertContains(response, 'No data to analyze!')

    def test_analyze_data(self):
        Stash.objects.create(user=self.user, name='Bank account',
                             date='2001-01-01', amount=1500)
        response = self.client.get('/9999-12-31/analyze_record/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['totalAmount'],
                         1500)