# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-22 05:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adsrental', '0077_auto_20180221_2037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='ban_reason',
            field=models.CharField(blank=True, choices=[('Google - Policy', 'Google - Policy'), ('Google - Billing', 'Google - Billing'), ('Google - Unresponsive User', 'Google - Unresponsive User'), ('Facebook - Policy', 'Facebook - Policy'), ('Facebook - Suspicious', 'Facebook - Suspicious'), ('Facebook - Lockout', 'Facebook - Lockout'), ('Facebook - Unresponsive User', 'Facebook - Unresponsive User'), ('Duplicate', 'Duplicate'), ('Bad ad account', 'Bad ad account'), ('Other', 'Other')], max_length=40, null=True),
        ),
    ]
