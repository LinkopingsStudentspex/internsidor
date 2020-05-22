# Generated by Django 3.0.6 on 2020-05-22 17:54

import batadasen.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AssociationGroupType',
            fields=[
                ('short_name', models.CharField(max_length=10, primary_key=True, serialize=False, verbose_name='kortnamn')),
                ('name', models.CharField(max_length=50, verbose_name='namn')),
                ('priority', models.IntegerField(default=0, verbose_name='prioritet')),
            ],
            options={
                'verbose_name': 'föreningsgrupptyp',
                'verbose_name_plural': 'föreningsgrupptyper',
            },
        ),
        migrations.CreateModel(
            name='AssociationYear',
            fields=[
                ('end_year', models.PositiveIntegerField(default=batadasen.models.get_current_assoc_year, primary_key=True, serialize=False, validators=[batadasen.models.validate_association_year], verbose_name='slutår')),
            ],
            options={
                'verbose_name': 'verksamhetsår',
                'verbose_name_plural': 'verksamhetsår',
            },
        ),
        migrations.CreateModel(
            name='Instrument',
            fields=[
                ('name', models.CharField(max_length=50, primary_key=True, serialize=False, verbose_name='instrument')),
            ],
            options={
                'verbose_name': 'instrument',
                'verbose_name_plural': 'instrument',
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('member_number', models.PositiveIntegerField(default=batadasen.models.Person.get_next_member_number, primary_key=True, serialize=False, verbose_name='medlemsnummer')),
                ('first_name', models.CharField(max_length=50, verbose_name='förnamn')),
                ('spex_name', models.CharField(blank=True, max_length=50, verbose_name='spexnamn')),
                ('last_name', models.CharField(max_length=50, verbose_name='efternamn')),
                ('maiden_name', models.CharField(blank=True, max_length=50, verbose_name='flicknamn')),
                ('street_address', models.CharField(blank=True, max_length=100, verbose_name='gatuadress')),
                ('postal_locality', models.CharField(blank=True, max_length=50, verbose_name='postort')),
                ('postal_code', models.CharField(blank=True, max_length=50, verbose_name='postnummer')),
                ('country', models.CharField(blank=True, max_length=50, verbose_name='land')),
                ('phone_home', models.CharField(blank=True, max_length=20, verbose_name='hemtelefon')),
                ('phone_work', models.CharField(blank=True, max_length=20, verbose_name='jobbtelefon')),
                ('phone_mobile', models.CharField(blank=True, max_length=20, verbose_name='mobiltelefon')),
                ('phone_extra', models.CharField(blank=True, max_length=20, verbose_name='extra telefon')),
                ('domestic_partner', models.IntegerField(blank=True, null=True, verbose_name='sambo')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True, verbose_name='mail')),
                ('address_list_email', models.EmailField(blank=True, help_text='Alternativ mailadress som ska visas istället i medlemslistor och liknande.', max_length=254, verbose_name='adresslistmail')),
                ('home_page', models.CharField(blank=True, max_length=100, verbose_name='hemsida')),
                ('wants_spexpressen', models.BooleanField(default=False, verbose_name='vill få spexpressen')),
                ('wants_spexinfo', models.BooleanField(default=True, verbose_name='vill få spexinfo-mail')),
                ('wants_spextjat', models.BooleanField(default=False, verbose_name='vill få spextjat-mail')),
                ('wants_trams', models.BooleanField(default=False, verbose_name='vill få trams-mail')),
                ('wants_blandat', models.BooleanField(default=True, verbose_name='vill få blandat-mail')),
                ('lifetime_member', models.BooleanField(default=False, verbose_name='livstidsmedlem')),
                ('honorary_member', models.BooleanField(default=False, verbose_name='hedersmedlem')),
                ('hundred_club', models.BooleanField(default=False, verbose_name='hundraklubben')),
                ('deceased', models.BooleanField(default=False, verbose_name='avliden')),
                ('address_changed_date', models.DateTimeField(blank=True, null=True, verbose_name='adress ändrad')),
                ('mail_changed_date', models.DateTimeField(blank=True, null=True, verbose_name='mail ändrad')),
                ('notes', models.TextField(blank=True, max_length=1000, null=True, verbose_name='övrigt')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='person', to=settings.AUTH_USER_MODEL, verbose_name='användare')),
            ],
            options={
                'verbose_name': 'person',
                'verbose_name_plural': 'personer',
            },
        ),
        migrations.CreateModel(
            name='Production',
            fields=[
                ('number', models.IntegerField(primary_key=True, serialize=False, verbose_name='nummer')),
                ('main_title', models.CharField(max_length=100, verbose_name='huvudtitel')),
                ('subtitle', models.CharField(blank=True, max_length=100, verbose_name='undertitel')),
                ('short_name', models.CharField(blank=True, max_length=20, verbose_name='kort namn')),
                ('year', models.PositiveIntegerField(validators=[batadasen.models.validate_production_year], verbose_name='år')),
                ('plot', models.TextField(blank=True, max_length=1000, verbose_name='handling')),
                ('closed', models.BooleanField(default=False, verbose_name='avslutad')),
                ('regular', models.BooleanField(default=True, verbose_name='ordinarie')),
                ('autumn', models.BooleanField(default=False, verbose_name='höstspex')),
            ],
            options={
                'verbose_name': 'uppsättning',
                'verbose_name_plural': 'uppsättningar',
            },
        ),
        migrations.CreateModel(
            name='ProductionGroupType',
            fields=[
                ('short_name', models.CharField(max_length=10, primary_key=True, serialize=False, verbose_name='kortnamn')),
                ('name', models.CharField(max_length=50, verbose_name='namn')),
                ('priority', models.IntegerField(default=0, verbose_name='prioritet')),
            ],
            options={
                'verbose_name': 'uppsättningsgrupptyp',
                'verbose_name_plural': 'uppsättningsgrupptyper',
            },
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('name', models.CharField(max_length=50, primary_key=True, serialize=False, verbose_name='namn')),
                ('email_alias', models.CharField(max_length=20, verbose_name='mailalias')),
                ('priority', models.IntegerField(default=0, verbose_name='prioritet')),
            ],
            options={
                'verbose_name': 'titel',
                'verbose_name_plural': 'titlar',
            },
        ),
        migrations.CreateModel(
            name='UserActivation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valid_until', models.DateTimeField(default=batadasen.models.calculate_expiration_time, verbose_name='giltig tills')),
                ('token', models.CharField(default=batadasen.models.generate_activation_token, max_length=50, verbose_name='token')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='batadasen.Person', verbose_name='person')),
            ],
        ),
        migrations.CreateModel(
            name='ProductionGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_type', models.ForeignKey(blank=True, help_text='lämna tomt om den här gruppen ska räknas som att vara med i en uppsättning utan att tillhöra en specifik grupp', null=True, on_delete=django.db.models.deletion.CASCADE, to='batadasen.ProductionGroupType', verbose_name='grupptyp')),
                ('production', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='batadasen.Production', verbose_name='uppsättning')),
            ],
            options={
                'verbose_name': 'uppsättningsgrupp',
                'verbose_name_plural': 'uppsättningsgrupper',
                'unique_together': {('production', 'group_type')},
            },
        ),
        migrations.CreateModel(
            name='EmailList',
            fields=[
                ('alias', models.CharField(max_length=20, primary_key=True, serialize=False, verbose_name='alias')),
                ('all_groups', models.ManyToManyField(blank=True, help_text='Denna lista kommer skicka mail till alla personer som någonsin har varit med i dessa grupper', related_name='email_lists', to='batadasen.ProductionGroupType', verbose_name='grupper av dessa typer i alla uppsättningar')),
                ('opt_in_members', models.ManyToManyField(blank=True, help_text='Vilka extra personer ska få mail från denna lista?', related_name='opt_in_email_lists', to='batadasen.Person', verbose_name='extramedlemmar')),
                ('opt_out_members', models.ManyToManyField(blank=True, help_text='Vilka personer ska inte få mail från denna lista, oavsett vilka grupper de är med i?', related_name='opt_out_email_lists', to='batadasen.Person', verbose_name='opt-out-medlemmar')),
                ('production_groups', models.ManyToManyField(blank=True, help_text='Denna lista kommer skicka mail till personer som är med i dessa uppsättningsgrupper', related_name='email_lists', to='batadasen.ProductionGroup', verbose_name='grupper från enskilda uppsättningar')),
                ('productions', models.ManyToManyField(blank=True, help_text='Denna lista kommer skicka mail till följande HELA uppsättningar', related_name='email_lists', to='batadasen.Production', verbose_name='hela uppsättningar')),
            ],
            options={
                'verbose_name': 'maillista',
                'verbose_name_plural': 'maillistor',
            },
        ),
        migrations.CreateModel(
            name='ProductionMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='batadasen.ProductionGroup', verbose_name='Grupp')),
                ('instrument', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='batadasen.Instrument', verbose_name='Instrument')),
                ('person', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='production_memberships', to='batadasen.Person', verbose_name='uppsättningsmedlemsskap')),
                ('title', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='batadasen.Title', verbose_name='Titel')),
            ],
            options={
                'verbose_name': 'uppsättningsmedlemskap',
                'verbose_name_plural': 'uppsättningsmedlemskap',
                'unique_together': {('person', 'group', 'title', 'instrument')},
            },
        ),
        migrations.CreateModel(
            name='ExtraEmail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, verbose_name='mail')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='extra_email', to='batadasen.Person', verbose_name='person')),
            ],
            options={
                'verbose_name': 'extra mailadress',
                'verbose_name_plural': 'extra mailadresser',
                'unique_together': {('person', 'email')},
            },
        ),
        migrations.CreateModel(
            name='AssociationMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='association_memberships', to='batadasen.Person', verbose_name='person')),
                ('year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='batadasen.AssociationYear', verbose_name='verksamhetsår')),
            ],
            options={
                'verbose_name': 'föreningsmedlemskap',
                'verbose_name_plural': 'föreningsmedlemskap',
                'unique_together': {('person', 'year')},
            },
        ),
        migrations.CreateModel(
            name='AssociationActivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('to_date', models.DateField(blank=True, null=True, verbose_name='till och med datum')),
                ('group_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='batadasen.AssociationGroupType', verbose_name='grupp')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='batadasen.Person', verbose_name='person')),
                ('title', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='batadasen.Title', verbose_name='titel')),
                ('year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='batadasen.AssociationYear', verbose_name='verksamhetsår')),
            ],
            options={
                'verbose_name': 'föreningsuppdrag',
                'verbose_name_plural': 'föreningsuppdrag',
                'unique_together': {('person', 'group_type')},
            },
        ),
    ]
