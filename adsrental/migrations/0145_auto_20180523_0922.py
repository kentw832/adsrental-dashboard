# Generated by Django 2.0.5 on 2018-05-23 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adsrental', '0144_auto_20180522_1104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leadaccount',
            name='account_type',
            field=models.CharField(choices=[('Facebook', 'Facebook'), ('Google', 'Google'), ('AMazon', 'Amazon')], max_length=50),
        ),
    ]
