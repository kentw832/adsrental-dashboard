# Generated by Django 2.0.3 on 2018-04-30 13:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adsrental', '0133_bundlerpaymentsreport_cancelled'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bundler',
            old_name='facebook_pay_split',
            new_name='facebook_parent_payment',
        ),
        migrations.RenameField(
            model_name='bundler',
            old_name='google_pay_split',
            new_name='google_parent_payment',
        ),
        migrations.AddField(
            model_name='bundler',
            name='parent_bundler',
            field=models.ForeignKey(blank=True, help_text='Bundler that gets part of the payment', null=True, on_delete=django.db.models.deletion.SET_NULL, to='adsrental.Bundler'),
        ),
    ]
