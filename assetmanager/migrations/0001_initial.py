# Generated by Django 2.1.1 on 2018-09-30 09:47

import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(unique=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Number')),
                ('purchase_time', models.CharField(blank=True, max_length=100, verbose_name='Purchase time')),
                ('purchase_price', models.CharField(blank=True, max_length=100, verbose_name='Purchase price')),
                ('standard_location', models.CharField(blank=True, max_length=100, verbose_name='Standard location')),
                ('supplier', models.CharField(blank=True, max_length=100, verbose_name='Supplier')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
            ],
        ),
        migrations.CreateModel(
            name='AssetModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('manufacturer', models.CharField(max_length=100, verbose_name='Manufacturer')),
                ('model_name', models.CharField(max_length=100, verbose_name='Model name')),
                ('model_description', models.TextField(blank=True, verbose_name='Model description')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
            ],
        ),
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=datetime.datetime.now, verbose_name='Timestamp')),
                ('notes', models.TextField(verbose_name='Notes')),
                ('new_status', models.CharField(choices=[('OK', 'OK'), ('DEG', 'Degraded'), ('OOO', 'Out of order'), ('UNK', 'Unknown'), ('HIST', 'Historical')], max_length=20, verbose_name='New status')),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='log_entries', to='assetmanager.Asset', verbose_name='Asset')),
            ],
        ),
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
            ],
        ),
        migrations.AddField(
            model_name='assetmodel',
            name='categories',
            field=models.ManyToManyField(related_name='asset_types', to='assetmanager.Category', verbose_name='Categories'),
        ),
        migrations.AddField(
            model_name='asset',
            name='model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='assets', to='assetmanager.AssetModel', verbose_name='Model'),
        ),
        migrations.AddField(
            model_name='asset',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='assets', to='assetmanager.Owner', verbose_name='Owner'),
        ),
    ]
