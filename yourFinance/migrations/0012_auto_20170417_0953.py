# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-17 07:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yourFinance', '0011_profile_costnames'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='costNames',
            field=models.TextField(default='Rent and other charges\nTransportation\nClothes\nFood\nHobby\nOthers\n'),
        ),
    ]
