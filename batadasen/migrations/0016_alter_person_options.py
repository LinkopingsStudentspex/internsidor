# Generated by Django 4.1.4 on 2024-10-05 17:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('batadasen', '0015_alter_person_options_person_medal_2_person_medal_4_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='person',
            options={'ordering': ['member_number'], 'permissions': [('view_private_info', 'Kan se all personinfo oavsett personens inställningar'), ('view_performances', 'Kan se loggade föreställnigar'), ('view_medal_candidates', 'Kan lista personer som är berättigade en årsmedalj')], 'verbose_name': 'person', 'verbose_name_plural': 'personer'},
        ),
    ]
