# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-07 20:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adsrental', '0084_auto_20180307_0905'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='adsdb_account_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
