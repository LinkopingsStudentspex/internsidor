# Generated by Django 3.0.7 on 2020-07-19 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('batadasen', '0012_auto_20200714_1701'),
    ]

    operations = [
        migrations.AddField(
            model_name='useractivation',
            name='provision_gsuite_account',
            field=models.BooleanField(default=False, verbose_name='aktivera Google-konto'),
        ),
    ]