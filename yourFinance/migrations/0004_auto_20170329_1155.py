# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-29 09:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourFinance', '0003_auto_20170329_1115'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='personaldata',
            name='user',
        ),
        migrations.RemoveField(
            model_name='stash',
            name='user',
        ),
        migrations.DeleteModel(
            name='PersonalData',
        ),
        migrations.DeleteModel(
            name='Stash',
        ),
    ]