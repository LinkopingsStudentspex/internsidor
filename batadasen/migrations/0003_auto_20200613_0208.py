# Generated by Django 3.0.6 on 2020-06-13 00:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('batadasen', '0002_auto_20200608_2304'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='domestic_partner',
        ),
        migrations.RemoveField(
            model_name='person',
            name='home_page',
        ),
        migrations.RemoveField(
            model_name='person',
            name='maiden_name',
        ),
        migrations.AddField(
            model_name='emaillist',
            name='all_titles',
            field=models.ManyToManyField(blank=True, help_text='Denna lista kommer skicka mail till personer som någonsin har haft dessa titlar', related_name='email_lists', to='batadasen.Title', verbose_name='alla personer med denna titel'),
        ),
        migrations.AddField(
            model_name='productionmembership',
            name='comment',
            field=models.CharField(blank=True, help_text='Här kan man skriva t.ex. vilket instrument en orkestermedlem spelar', max_length=100, verbose_name='kommentar'),
        ),
        migrations.AlterField(
            model_name='title',
            name='email_alias',
            field=models.CharField(blank=True, max_length=20, verbose_name='mailalias'),
        ),
        migrations.AlterUniqueTogether(
            name='productionmembership',
            unique_together={('person', 'group', 'title')},
        ),
        migrations.RemoveField(
            model_name='productionmembership',
            name='instrument',
        ),
        migrations.DeleteModel(
            name='Instrument',
        ),
    ]
