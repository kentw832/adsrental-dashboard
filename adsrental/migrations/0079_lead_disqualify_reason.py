# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-22 05:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adsrental', '0078_auto_20180222_0522'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='disqualify_reason',
            field=models.CharField(blank=True, choices=[("Doesn't meet friend requirements", "Doesn't meet friend requirements"), ("Doesn't meet age requirements", "Doesn't meet age requirements"), ('Fake FB', 'Fake FB'), ('Fake Google', 'Fake Google'), ('Non US account', 'Non US account'), ('Other', 'Other')], max_length=40, null=True),
        ),
    ]
