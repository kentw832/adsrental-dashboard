# Generated by Django 2.0.5 on 2018-06-11 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adsrental', '0152_bundlerleadstat'),
    ]

    operations = [
        migrations.AddField(
            model_name='ec2instance',
            name='is_essential',
            field=models.BooleanField(default=False, help_text='New global instance type, never stopped'),
        ),
    ]
