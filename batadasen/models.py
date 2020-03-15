from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import crypto, timezone

from datetime import timedelta


class Person(models.Model):
    class Meta:
        verbose_name = 'person'
        verbose_name_plural = 'personer'
    
    def get_next_member_number():
        # Gamla databasen använde speciella värden i medlemsnumret
        # 0-4999: riktiga medlemmar och livstidsmedlemmar
        # 5000-9999 temporära medlemsnummer, innan personen betalat medlemsavgift
        # 10000- ett par hedersmedlemmar
        # -99999 fyllt bakifrån med allehanda medlemmar, lite special- och testkonton och andra föreningar
        # För att inte förvirra någon i migreringen kommer alla behålla sina gamla nummer men vi kommer
        # fortsätta föreslå att fylla på från slutet på de vanliga (i skrivande stund nr 1086, det lär räcka ett tag)
        suggested_num = 1
        last_regular_member = Person.objects.filter(member_number__lt=5000).order_by('member_number').last()
        if last_regular_member is not None:
            suggested_num = last_regular_member.member_number + 1
            while Person.objects.filter(member_number=suggested_num).exists():
                suggested_num += 1

        return suggested_num
    
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='användare', related_name='person')

    member_number = models.PositiveIntegerField('medlemsnummer', default=get_next_member_number, primary_key=True)
    first_name = models.CharField('förnamn', max_length=50)
    spex_name = models.CharField('spexnamn', max_length=50, blank=True)
    last_name = models.CharField('efternamn', max_length=50)
    maiden_name = models.CharField('flicknamn', max_length=50, blank=True)
    street_address = models.CharField('gatuadress', max_length=100, blank=True)
    postal_locality = models.CharField('postort', max_length=50, blank=True)
    postal_code = models.CharField('postnummer', max_length=50, blank=True)
    country = models.CharField('land', max_length=50, blank=True)
    phone_home = models.CharField('hemtelefon', max_length=20, blank=True)
    phone_work = models.CharField('jobbtelefon', max_length=20, blank=True)
    phone_mobile = models.CharField('mobiltelefon', max_length=20, blank=True)
    phone_extra = models.CharField('extra telefon', max_length=20, blank=True)
    domestic_partner = models.IntegerField('sambo', null=True, blank=True)
    email = models.EmailField('mail', null=True, blank=True, unique=True)
    address_list_email = models.EmailField('adresslistmail', blank=True, help_text='Alternativ mailadress som ska visas istället i medlemslistor och liknande.')
    home_page = models.CharField('hemsida', max_length=100, blank=True)
    wants_spexpressen = models.BooleanField('vill få spexpressen', default=False)
    wants_spexinfo = models.BooleanField('vill få spexinfo-mail', default=True)
    wants_spextjat = models.BooleanField('vill få spextjat-mail', default=False)
    wants_trams = models.BooleanField('vill få trams-mail', default=False)
    wants_blandat = models.BooleanField('vill få blandat-mail', default=True)
    lifetime_member = models.BooleanField('livstidsmedlem', default=False)
    honorary_member = models.BooleanField('hedersmedlem', default=False)
    hundred_club = models.BooleanField('hundraklubben', default=False)
    deceased = models.BooleanField('avliden', default=False)
    address_changed_date = models.DateTimeField('adress ändrad', null=True, blank=True)
    mail_changed_date = models.DateTimeField('mail ändrad', null=True, blank=True)
    notes = models.TextField('övrigt', max_length=1000, null=True, blank=True)

    def __str__(self):
        if self.spex_name == '':
            return '({}) {} {}'.format(self.member_number, self.first_name, self.last_name)
        else:
            return '({}) {} "{}" {}'.format(self.member_number, self.first_name, self.spex_name, self.last_name)

def generate_activation_token():
    return crypto.get_random_string(length=50)

def calculate_expiration_time():
    return timezone.now() + timedelta(hours=2)

class UserActivation(models.Model):
    person = models.ForeignKey(Person, models.CASCADE, verbose_name='person')
    valid_until = models.DateTimeField('giltig tills', default=calculate_expiration_time)
    token = models.CharField('token', max_length=50, default=generate_activation_token)

    def __str__(self):
        return 'User activation for {}, {}, {}'.format(self.person, self.created_date, self.token)

class ExtraEmail(models.Model):
    class Meta:
        verbose_name = 'extra mailadress'
        verbose_name_plural = 'extra mailadresser'
        unique_together = ['person', 'email']
    
    person = models.ForeignKey(Person, models.CASCADE, verbose_name='person', related_name='extra_email')
    email = models.EmailField('mail')

    def __str__(self):
        return '{}: {}'.format(self.person, self.email)


def validate_production_year(year):
    if year < 1981:
        raise ValidationError('%(year)s är inte ett giltigt spexår, första spexet sattes upp 1981', params={'year': year})

class Production(models.Model):
    class Meta:
        verbose_name = 'uppsättning'
        verbose_name_plural = 'uppsättningar'

    number = models.IntegerField('nummer', primary_key=True, editable=True)
    main_title = models.CharField('huvudtitel', max_length=100)
    subtitle = models.CharField('undertitel', max_length=100, blank=True)
    short_name = models.CharField('kort namn', max_length=20, blank=True)
    year = models.PositiveIntegerField('år', validators=[validate_production_year])
    plot = models.TextField('handling', max_length=1000, blank=True)
    closed = models.BooleanField('avslutad', default=False)
    regular = models.BooleanField('ordinarie', default=True)
    autumn = models.BooleanField('höstspex', default=False)

    def __str__(self):
        return '{} - {} ({})'.format(self.number, self.main_title, self.short_name)


class Title(models.Model):
    class Meta:
        verbose_name = 'titel'
        verbose_name_plural = 'titlar'

    name = models.CharField('namn', max_length=50, primary_key=True)
    email_alias = models.CharField('mailalias', max_length=20)
    priority = models.IntegerField('prioritet', default=0)

    def __str__(self):
        return self.name
    

class Group(models.Model):
    class Meta:
        verbose_name = 'grupp'
        verbose_name_plural = 'grupper'
    
    short_name = models.CharField('kortnamn', max_length=10, primary_key=True)
    name = models.CharField('namn', max_length=50)
    priority = models.IntegerField('prioritet', default=0)
    
    def __str__(self):
        return '{} - {}'.format(self.short_name, self.name)


def validate_association_year(year):
    if year <= 1978:
        raise ValidationError('%(year)s är inte ett giltigt verksamhetsår, föreningen bildades 1978', params={'year': '{}/{}'.format(year-1, year)})

def get_current_assoc_year():
    today = datetime.date.today()
    if today > datetime.date(today.year, 6, 30):
        return today.year + 1
    else:
        return today.year

class AssociationYear(models.Model):
    class Meta:
        verbose_name = 'verksamhetsår'
        verbose_name_plural = 'verksamhetsår'

    end_year = models.PositiveIntegerField('slutår', default=get_current_assoc_year, validators=[validate_association_year], primary_key=True)

    def get_start_time(self):
        return datetime.datetime(self.end_year-1, 7, 1, 0, 0, 0)
    
    def get_end_time(self):
        return datetime.datetime(self.end_year, 6, 30, 23, 59, 59)

    def __str__(self):
        return '{}/{}'.format(self.end_year % 100 -1, self.end_year % 100)
    

class AssociationActivity(models.Model):
    class Meta:
        verbose_name = 'föreningsuppdrag'
        verbose_name_plural = 'föreningsuppdrag'
        unique_together = [['person', 'group']]

    person = models.ForeignKey(Person, models.CASCADE, verbose_name='person')
    group = models.ForeignKey(Group, models.CASCADE, verbose_name='grupp')
    title = models.ForeignKey(Title, models.CASCADE, null=True, verbose_name='titel')
    year = models.ForeignKey(AssociationYear, models.CASCADE, verbose_name='verksamhetsår')
    to_date = models.DateField('till och med datum', null=True, blank=True)

    def __str__(self):
        if self.title is None:
            return '{}: {} {} ({})'.format(self.person, self.group, self.year, self.title)
        else:
            return '{}: {} {}'.format(self.person, self.group, self.year)
    

class ProductionGroup(models.Model):
    class Meta:
        verbose_name = 'uppsättningsgrupp'
        verbose_name_plural = 'uppsättningsgrupper'
        unique_together = ['production', 'group']

    production = models.ForeignKey(Production, models.CASCADE, verbose_name='uppsättning')
    group = models.ForeignKey(Group, models.CASCADE, verbose_name='grupp', null=True, blank=True, help_text='lämna tomt om personen är med i en uppsättning utan att vara med i en specifik grupp')

    def __str__(self):
        if self.group is None:
            if self.production.short_name == '':
                return '{} (ingen grupp)'.format( self.production.year)
            else:
                return '{} (ingen grupp)'.format( self.production.short_name)
        else:
            return '{}-{}'.format(self.group.short_name, self.production.year % 100)
    

class Instrument(models.Model):
    class Meta:
        verbose_name = 'instrument'
        verbose_name_plural = 'instrument'

    name = models.CharField('instrument', max_length=50, primary_key=True)

    def __str__(self):
        return self.name


class ProductionMembership(models.Model):
    class Meta:
        verbose_name = 'uppsättningsmedlemskap'
        verbose_name_plural = 'uppsättningsmedlemskap'
        unique_together = [['person', 'group', 'title', 'instrument']]

    person = models.ForeignKey(Person, models.CASCADE, related_name='uppsättningsmedlemsskap', editable=False)
    group = models.ForeignKey(ProductionGroup, models.CASCADE)
    title = models.ForeignKey(Title, models.SET_NULL, null=True, blank=True)
    instrument = models.ForeignKey(Instrument, models.SET_NULL, null=True, blank=True)

    def __str__(self):
        titles = []
        if self.title is not None:
            titles.append(self.title.name)
        if self.instrument is not None:
            titles.append(self.instrument.name)

        if len(titles) > 0:
            title_str = ', '.join(titles)
            return '{}: {} ({})'.format(self.person.member_number, self.group, title_str)
        else:
            return '{}: {}'.format(self.person.member_numer, self.group)

    
class EmailList(models.Model):
    class Meta:
        verbose_name = 'maillista'
        verbose_name_plural = 'maillistor'

    alias = models.CharField('alias', max_length=20, primary_key=True)
    opt_in_members = models.ManyToManyField(
        Person, 
        verbose_name='extramedlemmar', 
        related_name='opt_in_email_lists', 
        blank=True,
        help_text='Vilka extra personer ska få mail från denna lista?')
    opt_out_members = models.ManyToManyField(
        Person, 
        verbose_name='opt-out-medlemmar', 
        related_name='opt_out_email_lists', 
        blank=True,
        help_text='Vilka personer ska inte få mail från denna lista, oavsett vilka grupper de är med i?')
    all_groups = models.ManyToManyField(
        Group, 
        related_name='maillistor', 
        verbose_name='grupper i alla uppsättningar', 
        blank=True,
        help_text='Denna lista kommer skicka mail till alla personer som någonsin har varit med i dessa grupper')
    production_groups = models.ManyToManyField(
        ProductionGroup, 
        related_name='maillistor', 
        verbose_name='grupper från enskilda uppsättningar', 
        blank=True,
        help_text='Denna lista kommer skicka mail till personer som är med i dessa uppsättningsgrupper')
    productions = models.ManyToManyField(
        Production, 
        related_name='maillistor', 
        verbose_name='hela uppsättningar', 
        blank=True,
        help_text='Denna lista kommer skicka mail till följande HELA uppsättningar')

    def __str__(self):
        return self.alias
    

class AssociationMembership(models.Model):
    person = models.ForeignKey(Person, models.CASCADE, verbose_name='person')
    year = models.ForeignKey(AssociationYear, models.CASCADE, verbose_name='verksamhetsår')

    def __str__(self):
        return '{} var medlem {}'.format(self.person, self.year)
    
    class Meta:
        verbose_name = 'föreningsmedlemskap'
        verbose_name_plural = 'föreningsmedlemskap'
        
        unique_together = ['person', 'year']
