# Generated by Django 3.0.6 on 2020-06-08 21:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('batadasen', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='associationactivity',
            name='title',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='batadasen.Title', verbose_name='titel'),
        ),
        migrations.AlterField(
            model_name='associationmembership',
            name='year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='batadasen.AssociationYear', verbose_name='verksamhetsår'),
        ),
    ]
