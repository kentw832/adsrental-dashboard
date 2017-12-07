# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-12-07 18:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('adsrental', '0012_auto_20171207_0434'),
    ]

    operations = [
        migrations.AddField(
            model_name='raspberrypi',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='raspberrypi',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
