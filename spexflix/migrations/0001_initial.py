# Generated by Django 3.0.5 on 2020-04-18 23:22

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import spexflix.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Production',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(help_text='Vanligtvis året (t.ex 2019) men kan också vara något annat som identifierar en speciell uppsättning (t.ex SM-17 eller Jubel-35)', max_length=10, verbose_name='Kortnamn')),
                ('title', models.CharField(max_length=200, verbose_name='Titel')),
                ('subtitle', models.CharField(blank=True, max_length=200, verbose_name='Undertitel')),
                ('poster_image', models.ImageField(blank=True, null=True, upload_to=spexflix.models.get_poster_upload_path, verbose_name='Omslagsbild')),
            ],
            options={
                'verbose_name': 'Uppsättning',
                'verbose_name_plural': 'Uppsättningar',
            },
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Vad är detta för video? Typiskt "Föreställning" eller "Spexialmaterial" eller liknande', max_length=200, verbose_name='Videotitel')),
                ('video_file', models.FileField(upload_to=spexflix.models.get_video_upload_path, validators=[django.core.validators.FileExtensionValidator(['webm'])], verbose_name='Fil')),
                ('information', models.TextField(blank=True, help_text='Ytterligare information om videon, t.ex inspelningsdatum, plats eller vem som har gjort klipping etc', max_length=500, verbose_name='Information')),
                ('production', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='videos', to='spexflix.Production', verbose_name='Uppsättning')),
            ],
            options={
                'verbose_name': 'Video',
                'verbose_name_plural': 'Videos',
            },
        ),
        migrations.CreateModel(
            name='SubtitleTrack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='Namn')),
                ('subtitle_file', models.FileField(upload_to=spexflix.models.get_subtitle_upload_path, validators=[django.core.validators.FileExtensionValidator(['vtt'])], verbose_name='Fil')),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subtitles', to='spexflix.Video', verbose_name='Video')),
            ],
            options={
                'verbose_name': 'Undertextspår',
                'verbose_name_plural': 'Undertextspår',
            },
        ),
    ]
