# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-01-19 02:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adsrental', '0027_auto_20180119_0200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='raspberry_pi',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='adsrental.RaspberryPi'),
        ),
    ]
