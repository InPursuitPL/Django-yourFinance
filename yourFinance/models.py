from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Stash(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=20)
    date = models.DateField()
    amount = models.FloatField()

    def __str__(self):
        return '{} {} {}'.format(self.name, self.date, self.amount)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stashNames = models.TextField(default='Bank account\nSavings\nWallet\nOthers\n')
    costNames = models.TextField(default='Rent and other charges\nTransportation\n'
                                         'Clothes\nFood\nHobby\nOthers')
    existenceLevel = models.DecimalField(verbose_name='Existence level monthly cost',
                                         default=1500.00,
                                         max_digits=8,
                                         decimal_places=2)
    minimalLevel = models.DecimalField(verbose_name='Minimal level monthly cost',
                                       default=2000.00,
                                       max_digits=8,
                                       decimal_places=2)
    standardLevel = models.DecimalField(verbose_name='Standard level monthly cost',
                                        default=3000.00,
                                        max_digits=8,
                                        decimal_places=2)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()