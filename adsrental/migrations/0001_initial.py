# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-12-05 00:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('leadid', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('email', models.CharField(blank=True, max_length=255, null=True)),
                ('phone', models.CharField(blank=True, max_length=255, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('account_name', models.CharField(max_length=255)),
                ('usps_tracking_code', models.CharField(blank=True, max_length=255, null=True)),
                ('utm_source', models.CharField(blank=True, max_length=80, null=True)),
                ('google_account', models.IntegerField()),
                ('facebook_account', models.IntegerField()),
            ],
            options={
                'db_table': 'lead',
            },
        ),
        migrations.CreateModel(
            name='RaspberryPi',
            fields=[
                ('rpid', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('leadid', models.CharField(blank=True, max_length=255, null=True)),
                ('ipaddress', models.CharField(max_length=255)),
                ('ec2_hostname', models.CharField(blank=True, max_length=255, null=True)),
                ('first_seen', models.DateTimeField()),
                ('last_seen', models.DateTimeField()),
                ('tunnel_last_tested', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'raspberry_pi',
            },
        ),
    ]
