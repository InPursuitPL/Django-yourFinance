# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-15 08:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yourFinance', '0010_auto_20170414_0957'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='costNames',
            field=models.TextField(default='Rent and other charges\nTransportation\nClothes\nFood\nHobby\nOthers'),
        ),
    ]