# Generated by Django 2.0.3 on 2018-03-26 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adsrental', '0096_auto_20180326_0604'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leadaccount',
            name='active',
            field=models.BooleanField(default=True, help_text='If false, entry considered as deleted'),
        ),
    ]
