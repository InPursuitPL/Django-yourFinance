import re

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .models import Stash, Profile


class PeriodForm(forms.Form):
    startDate = forms.DateField(label='Start date', required=False)
    endDate = forms.DateField(label='End date', required=False)

class DateForm(forms.Form):
    date = forms.DateField(required=False)

class NameForm(forms.Form):
    name = forms.CharField(max_length=30, required=False)

class StashWithoutDateForm(forms.ModelForm):
    class Meta:
        model = Stash
        fields = ('name', 'amount')

class StashForm(forms.ModelForm):
    class Meta:
        model = Stash
        fields = ('date', 'name', 'amount')

class MonthlyCostsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('existenceLevel', 'minimalLevel', 'standardLevel')


class RegistrationForm(forms.Form):
    username = forms.CharField(label='User name', max_length=30)
    email = forms.EmailField(label='E-mail')
    password1 = forms.CharField(label='Password',
                          widget=forms.PasswordInput())
    password2 = forms.CharField(label='Password (again)',
                        widget=forms.PasswordInput())

    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
            if password1 == password2:
                return password2
        raise forms.ValidationError('Passwords do not match.')

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.search(r'^\w+$', username):
            raise forms.ValidationError('Username can only contain\
alphanumeric characters and the underscore.')
        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            return username
        raise forms.ValidationError('Username is already taken.', code='invalid')

class CostGroupsForm(forms.Form):
  amount = forms.FloatField()
  name = forms.CharField(widget=forms.HiddenInput())
