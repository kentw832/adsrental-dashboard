# Generated by Django 2.0.6 on 2018-06-21 00:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adsrental', '0165_lead_is_reimbursed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ec2instance',
            name='browser_type',
            field=models.CharField(choices=[('Unknown', 'Unknown'), ('MLA', 'Multilogin App 2.1.4'), ('Antidetect', 'Antidetect 7.3.1'), ('Antidetect 7.3.2', 'Antidetect 7.3.2')], default='Unknown', help_text='Browser used on EC2', max_length=20),
        ),
    ]
