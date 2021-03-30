# Generated by Django 3.0.7 on 2021-03-30 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('batadasen', '0013_useractivation_provision_gsuite_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='email_active',
            field=models.BooleanField(default=True, help_text='Är personens mailadress aktiv och fungerande? Om denna ruta kryssas ur kommer personen inte längre få några brev från spexets maillistor.', verbose_name='mailadress aktiv'),
        ),
    ]
