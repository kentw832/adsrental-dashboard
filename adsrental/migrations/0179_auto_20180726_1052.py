# Generated by Django 2.0.7 on 2018-07-26 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adsrental', '0178_leadhistorymonth_note'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='account_name',
            field=models.CharField(blank=True, help_text='Obsolete, was used in SF, should be removed', max_length=255, null=True),
        ),
    ]
