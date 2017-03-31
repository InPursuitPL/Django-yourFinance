from django.db import models
from django.contrib.auth.models import User
#from django.conf import settings

class Stash(models.Model):
    NAME_CHOICES = (
        ('Bank account', 'bank acc'),
        ('Savings', 'savings'),
        ('Wallet', 'wallet'),
        ('Others', 'others'),
    )
    user = models.ForeignKey(User)
    #user = models.ForeignKey(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length=20, choices=NAME_CHOICES)
    date = models.DateField()
    amount = models.FloatField()