# Generated by Django 2.1.7 on 2019-08-26 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adsrental', '0254_auto_20190823_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='has_active_accounts',
            field=models.BooleanField(default=True, help_text='Lead has active lead accounts.'),
        ),
    ]
