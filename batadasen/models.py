from datetime import timedelta, datetime, date
import re

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.signals import post_save
from django.db.models import Q
from django.dispatch import receiver
from django.utils import crypto, timezone


def get_current_assoc_end_year():
    today = date.today()
    if today > date(today.year, 6, 30):
        return today.year + 1
    else:
        return today.year

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


class Person(models.Model):
    class Meta:
        verbose_name = 'person'
        verbose_name_plural = 'personer'
        ordering = ['member_number']
        permissions = [
            ("view_private_info", "Kan se all personinfo oavsett personens inställningar")
        ]
    
    class PrivacySetting(models.TextChoices):
        PRIVATE = 'PVT', 'Privat', # Only number is visible.
        LIMITED = 'LIM', 'Begränsad', # Other members can see name and email. Default.
        OPEN = 'OPN', 'Öppen' # Other members can see everything.
    
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='användare', related_name='person')

    member_number = models.PositiveIntegerField('medlemsnummer', default=get_next_member_number, primary_key=True)
    first_name = models.CharField('förnamn', max_length=50)
    spex_name = models.CharField('spexnamn', max_length=50, blank=True)
    last_name = models.CharField('efternamn', max_length=50)
    street_address = models.CharField('gatuadress', max_length=100, blank=True)
    postal_locality = models.CharField('postort', max_length=50, blank=True)
    postal_code = models.CharField('postnummer', max_length=50, blank=True)
    country = models.CharField('land', max_length=50, blank=True)
    phone_home = models.CharField('hemtelefon', max_length=50, blank=True)
    phone_work = models.CharField('jobbtelefon', max_length=50, blank=True)
    phone_mobile = models.CharField('mobiltelefon', max_length=50, blank=True)
    phone_extra = models.CharField('extra telefon', max_length=50, blank=True)
    email = models.EmailField('mail', null=True, blank=True, unique=True, help_text='Hit kommer mail från spexets maillistor skickas.')
    address_list_email = models.EmailField('visningsmail', blank=True, help_text='Alternativ mailadress som ska visas istället i medlemslistor och liknande.')
    wants_spexpressen = models.BooleanField('vill få spexpressen', default=False)
    wants_spexinfo = models.BooleanField('vill få spexinfo-mail', default=True)
    wants_trams = models.BooleanField('vill få trams-mail', default=False)
    wants_blandat = models.BooleanField('vill få blandat-mail', default=True)
    lifetime_member = models.BooleanField('livstidsmedlem', default=False)
    honorary_member = models.BooleanField('hedersmedlem', default=False)
    hundred_club = models.BooleanField('hundraklubben', default=False)
    deceased = models.BooleanField('avliden', default=False)
    address_changed_date = models.DateTimeField('adress ändrad', null=True, blank=True)
    mail_changed_date = models.DateTimeField('mail ändrad', null=True, blank=True)
    notes = models.TextField('övrigt', max_length=1000, null=True, blank=True)
    privacy_setting = models.CharField(
        'sekretessnivå', 
        max_length=3, 
        choices=PrivacySetting.choices, 
        default=PrivacySetting.LIMITED, 
        help_text='Privat: endast administratörer kan se dina personuppgifter. '
                  'Begränsad: andra inloggade kan se namn och epostadress. '
                  'Öppen: andra inloggade kan se all din information. '
                  'Inga personuppgifter kommer någonsin vara synliga för icke-inloggade.')

    @property
    def full_name(self):
        if self.spex_name == '':
            return '{} {}'.format(self.first_name, self.last_name)
        else:
            return '{} "{}" {}'.format(self.first_name, self.spex_name, self.last_name)

    def __str__(self):
        return '({}) {}'.format(self.member_number, self.full_name)
    
    @property
    def currently_member(self):
        if self.lifetime_member or self.honorary_member:
            return True
        
        return self.association_memberships.filter(year=get_current_assoc_year()).exists()
    
    @property
    def display_email(self):
        if self.address_list_email != '':
            return self.address_list_email
        else:
            return self.email

    # Validates case-insensitive email address uniqueness
    def validate_unique(self, exclude=None):
        if Person.objects.exclude(member_number=self.member_number).filter(email__iexact=self.email).exists():
            raise ValidationError({'email': 'En person med denna mailadress finns redan.'})
        super(Person, self).validate_unique(exclude)
        

def generate_activation_token():
    return crypto.get_random_string(length=50)

def calculate_expiration_time():
    return timezone.now() + timedelta(hours=2)

class UserActivation(models.Model):
    class Meta:
        verbose_name = 'användaraktivering'
        verbose_name_plural = 'användaraktiveringar'
        ordering = ['person']
    person = models.ForeignKey(Person, models.CASCADE, verbose_name='person')
    valid_until = models.DateTimeField('giltig tills', default=calculate_expiration_time)
    token = models.CharField('token', max_length=50, default=generate_activation_token)

    def __str__(self):
        return 'User activation for {}, valid until {}'.format(self.person, self.valid_until)

class ExtraEmail(models.Model):
    class Meta:
        verbose_name = 'extra mailadress'
        verbose_name_plural = 'extra mailadresser'
        unique_together = ['person', 'email']
        ordering = ['person']
    
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
        ordering = ['number']

    number = models.IntegerField('nummer', primary_key=True, editable=True)
    main_title = models.CharField('huvudtitel', max_length=100)
    subtitle = models.CharField('undertitel', max_length=100, blank=True)
    short_name = models.CharField('kort namn', max_length=50, blank=True)
    year = models.PositiveIntegerField('år', validators=[validate_production_year])
    plot = models.TextField('handling', max_length=1000, blank=True)
    closed = models.BooleanField('avslutad', default=False)
    regular = models.BooleanField('ordinarie', default=True)
    autumn = models.BooleanField('höstspex', default=False)

    def __str__(self):
        if self.short_name == '':
            return '{} - {} ({})'.format(self.number, self.main_title, self.year)
        else:
            return '{} - {} ({})'.format(self.number, self.main_title, self.short_name)

DIRECTION_TITLES = [
    'Directeur',
    'Direktör',
    'Ekonomichef',
    'Producent'
]

class Title(models.Model):
    class Meta:
        verbose_name = 'titel'
        verbose_name_plural = 'titlar'
        ordering = ['name']

    name = models.CharField('namn', max_length=50, primary_key=True)
    email_alias = models.CharField('mailalias', max_length=50, blank=True)
    priority = models.IntegerField('prioritet', default=0)

    def __str__(self):
        return self.name
    

class ProductionGroupType(models.Model):
    class Meta:
        verbose_name = 'uppsättningsgrupptyp'
        verbose_name_plural = 'uppsättningsgrupptyper'
        ordering = ['short_name']
    
    short_name = models.CharField('kortnamn', max_length=50, primary_key=True)
    name = models.CharField('namn', max_length=50)
    priority = models.IntegerField('prioritet', default=0)
    exclude_from_production_email = models.BooleanField('uteslut från uppsättningslistor', default=False, help_text='Uteslut grupper av denna typ från att vara med på maillistor för hela uppsättningar?')
    
    def __str__(self):
        return "{} ({})".format(self.name, self.short_name)


def validate_association_year(year):
    if year <= 1978:
        raise ValidationError('%(year)s är inte ett giltigt verksamhetsår, föreningen bildades 1978', params={'year': '{}/{}'.format(year-1, year)})

class AssociationYear(models.Model):
    class Meta:
        verbose_name = 'verksamhetsår'
        verbose_name_plural = 'verksamhetsår'
        ordering = ['end_year']

    end_year = models.PositiveIntegerField('slutår', default=get_current_assoc_end_year, validators=[validate_association_year], primary_key=True)

    def get_start_time(self):
        return datetime.datetime(self.end_year-1, 7, 1, 0, 0, 0)
    
    def get_end_time(self):
        return datetime.datetime(self.end_year, 6, 30, 23, 59, 59)

    def __str__(self):
        return '{:02}/{:02}'.format((self.end_year - 1) % 100, self.end_year % 100)
    

def get_current_assoc_year():
    return AssociationYear.objects.get(end_year=get_current_assoc_end_year())
    

class AssociationGroupType(models.Model):
    class Meta:
        verbose_name = 'föreningsgrupptyp'
        verbose_name_plural = 'föreningsgrupptyper'
        ordering = ['short_name']
    
    short_name = models.CharField('kortnamn', max_length=10, primary_key=True)
    name = models.CharField('namn', max_length=50)
    priority = models.IntegerField('prioritet', default=0)
    
    def __str__(self):
        return self.name


class AssociationGroup(models.Model):
    class Meta:
        verbose_name = 'föreningsgrupp'
        verbose_name_plural = 'föreningsgrupp'
        unique_together = [['year', 'group_type']]
        ordering = ['group_type','year']
    
    year = models.ForeignKey(AssociationYear, models.CASCADE, verbose_name='verksamhetsår', related_name='groups')
    group_type = models.ForeignKey(AssociationGroupType, models.CASCADE, verbose_name='grupptyp')

    def __str__(self):
        return '{} {}'.format(self.group_type.short_name, self.year)


class AssociationActivity(models.Model):
    class Meta:
        verbose_name = 'föreningsuppdrag'
        verbose_name_plural = 'föreningsuppdrag'
        unique_together = [['person', 'group']]
        ordering = ['person', 'group']

    person = models.ForeignKey(Person, models.CASCADE, verbose_name='person', related_name='association_activities')
    group = models.ForeignKey(AssociationGroup, models.CASCADE, verbose_name='grupp', related_name='activities')
    title = models.ForeignKey(Title, models.SET_NULL, null=True, blank=True, verbose_name='titel')
    to_date = models.DateField('till och med datum', null=True, blank=True)

    def __str__(self):
        if self.title is None:
            return '{}: {}'.format(self.person, self.group)
        else:
            return '{}: {} ({})'.format(self.person, self.group, self.title)
    

class ProductionGroup(models.Model):
    class Meta:
        verbose_name = 'uppsättningsgrupp'
        verbose_name_plural = 'uppsättningsgrupper'
        unique_together = ['production', 'group_type']
        ordering = ['group_type','production']

    production = models.ForeignKey(Production, models.CASCADE, verbose_name='uppsättning', related_name='groups')
    group_type = models.ForeignKey(ProductionGroupType, models.CASCADE, verbose_name='grupptyp', null=True, blank=True, help_text='lämna tomt om den här gruppen ska räknas som att vara med i en uppsättning utan att tillhöra en specifik grupp', related_name='group_instances')

    def __str__(self):
        if self.group_type is None:
            if self.production.short_name == '':
                return '{} (ingen grupp)'.format( self.production.year)
            else:
                return '{} (ingen grupp)'.format( self.production.short_name)
        else:
            return '{}-{:02}'.format(self.group_type.short_name, self.production.year % 100)
    
    # Eftersom NULL-värden aldrig är lika med varandra så funkar inte ovanstående unique_together
    # och vi måste validera fallet när man försöker skapa två uppsättningsgrupper utan grupptyp 
    # i samma uppsättning.
    def validate_unique(self, exclude=None):
        if self.group_type is None and ProductionGroup.objects.exclude(id=self.id).filter(production=self.production, group_type__isnull=True).exists():
            raise ValidationError("En uppsättningsgrupp utan grupptyp finns redan i denna uppsättning")
        super(ProductionGroup, self).validate_unique(exclude)
    

class ProductionMembership(models.Model):
    class Meta:
        verbose_name = 'uppsättningsmedlemskap'
        verbose_name_plural = 'uppsättningsmedlemskap'
        unique_together = [['person', 'group', 'title']]
        ordering = ['person', 'group__production']

    person = models.ForeignKey(Person, models.CASCADE, verbose_name='uppsättningsmedlemsskap', related_name='production_memberships', editable=False)
    group = models.ForeignKey(ProductionGroup, models.CASCADE, verbose_name='Grupp', related_name='memberships')
    title = models.ForeignKey(Title, models.SET_NULL, null=True, blank=True, verbose_name='Titel')
    comment = models.CharField(max_length=100, blank=True, verbose_name='kommentar', help_text='Här kan man skriva t.ex. vilket instrument en orkestermedlem spelar')

    def short_description(self):
        titles = []
        if self.title is not None:
            titles.append(self.title.name)

        if len(titles) > 0:
            title_str = ', '.join(titles)
            return '{} ({})'.format(self.group, title_str)
        else:
            return str(self.group)

    def __str__(self):
        return '{}: {}'.format(self.person.member_number, self.short_description())

    
class EmailList(models.Model):
    class Meta:
        verbose_name = 'maillista'
        verbose_name_plural = 'maillistor'
        ordering = ['alias']

    alias = models.CharField('alias', max_length=50, primary_key=True, help_text='Namnet på listan, det som står framför @')

    is_internal = models.BooleanField('intern lista', default=True, help_text="Ska endast spexare få skicka till denna lista?")

    forward_to = models.ForeignKey(
        'self',
        models.SET_NULL,
        verbose_name='vidarebefordring till annan lista',
        related_name='list_forwardings',
        null=True,
        blank=True,
        help_text='Ska mail till denna lista skickas vidare till medlemmar i en annan lista?')

    opt_in_members = models.ManyToManyField(
        Person, 
        verbose_name='enskilda personer',
        related_name='opt_in_email_lists', 
        blank=True,
        help_text='Vilka enskilda personer ska få mail från denna lista?')
    opt_out_members = models.ManyToManyField(
        Person, 
        verbose_name='opt-out-medlemmar', 
        related_name='opt_out_email_lists', 
        blank=True,
        help_text='Vilka personer ska inte få mail från denna lista, oavsett vilka grupper de är med i?')

    # Production lists
    all_groups = models.ManyToManyField(
        ProductionGroupType, 
        related_name='email_lists', 
        verbose_name='grupper av dessa typer i alla uppsättningar', 
        blank=True,
        help_text='Denna lista kommer skicka mail till alla personer som någonsin har varit med i dessa grupper')
    production_groups = models.ManyToManyField(
        ProductionGroup, 
        related_name='email_lists', 
        verbose_name='grupper från enskilda uppsättningar', 
        blank=True,
        help_text='Denna lista kommer skicka mail till personer som är med i dessa uppsättningsgrupper')
    productions = models.ManyToManyField(
        Production, 
        related_name='email_lists', 
        verbose_name='hela uppsättningar', 
        blank=True,
        help_text='Denna lista kommer skicka mail till följande HELA uppsättningar, förutom i de fall då listans namn slutar med \"gruppledare\".')
    
    # Association lists
    active_association_groups = models.ManyToManyField(
        AssociationGroupType,
        related_name='email_lists',
        verbose_name='föreningsgrupper för aktivt verksamhetsår',
        blank=True,
        help_text='Denna lista kommer skicka mail till dessa aktiva föreningsgrupper')
    association_groups = models.ManyToManyField(
        AssociationGroup,
        related_name='email_lists',
        verbose_name='föreningsgrupper från enskilda verksamhetsår',
        blank=True,
        help_text='Denna lista kommer skicka mail till personer som var med i dessa föreningsgrupper ett visst år')
    
    # Title lists
    all_titles = models.ManyToManyField(
        Title,
        related_name='email_lists',
        verbose_name='alla personer med denna titel',
        blank=True,
        help_text='Denna lista kommer skicka mail till personer som någonsin har haft dessa titlar')

    def __str__(self):
        return self.alias
    
    @property
    def recipients(self):
        person_set = set()

        valid_email_regex = r'^[^@]+@[^@]+$'
        pattern = re.compile(valid_email_regex)
        valid_email = Q(email__regex=valid_email_regex)
        valid_persons = Person.objects.filter(valid_email)

        for person in self.opt_in_members.filter(valid_email):
            person_set.add(person)
        
        if self.forward_to is not None:
            person_set.update(self.forward_to.recipients)

        for group_type in self.all_groups.all():
            for person in valid_persons.filter(production_memberships__group__group_type=group_type):
                person_set.add(person)
        
        for group in self.production_groups.all():
            for person in valid_persons.filter(production_memberships__group=group):
                person_set.add(person)
            
            # Add the current direction to the production group lists
            for person in valid_persons.filter(production_memberships__group__production=group.production, production_memberships__title__in=DIRECTION_TITLES):
                person_set.add(person)
        
        for production in self.productions.all():
            # Special handling of email lists to group leaders
            if self.alias.endswith('gruppledare'):
                for person in valid_persons.filter(production_memberships__group__production=production, production_memberships__title='Gruppledare'):
                    person_set.add(person)
            else:
                for person in valid_persons.filter(
                    production_memberships__group__production=production,
                    production_memberships__group__group_type__exclude_from_production_email=False):
                    person_set.add(person)
        
        for group in self.association_groups.all():
            for person in valid_persons.filter(association_activities__group=group):
                person_set.add(person)
        
        for title in self.all_titles.all():
            for person in valid_persons.filter(Q(production_memberships__title=title) | Q(association_activities__title=title)):
                person_set.add(person)
        
        current_assoc_year = get_current_assoc_year()

        for group_type in self.active_association_groups.all():
            for person in valid_persons.filter(association_activities__group__group_type=group_type, association_activities__group__year=current_assoc_year):
                person_set.add(person)
        
        # Additional includes for special lists
        if self.alias == 'kallelse':
            for membership in current_assoc_year.memberships.all():
                if membership.person.email is not None and re.fullmatch(pattern, membership.person.email) is not None:
                    person_set.add(membership.person)
        elif self.alias == 'spexinfo':
            for person in valid_persons.filter(wants_spexinfo=True):
                person_set.add(person)
        elif self.alias == 'blandat':
            for person in valid_persons.filter(wants_blandat=True):
                person_set.add(person)
        elif self.alias == 'trams':
            for person in valid_persons.filter(wants_trams=True):
                person_set.add(person)
        elif self.alias == 'styrelse-kallelse':
            active_productions = Production.objects.filter(closed=False)
            for active_production in active_productions:
                # Active 'directions'
                for person in valid_persons.filter(production_memberships__group__production__closed=False, production_memberships__title__in=DIRECTION_TITLES):
                    person_set.add(person)
                # Auditors for active productions
                for person in valid_persons.filter(production_memberships__group__production__closed=False, production_memberships__group__group_type__short_name='REV'):
                    person_set.add(person)

            for activity in current_assoc_year.groups.get(Q(group_type__short_name='STYR') | Q(group_type__short_name='REV')).activities.all():
                if activity.person.email is not None and re.fullmatch(pattern, activity.person.email) is not None:
                    person_set.add(activity.person)
        
        # Direct title-specific emails to the currently active title holder.
        # Currently only for board members.
        try:
            title = Title.objects.get(email_alias=self.alias)
            for activity in current_assoc_year.groups.get(group_type__short_name='STYR').activities.filter(title=title):
                if activity.person.email is not None and re.fullmatch(pattern, activity.person.email) is not None:
                    person_set.add(activity.person)
        except Title.DoesNotExist:
            pass

        # Last of all, handle opt out requests
        for person in self.opt_out_members.all():
            person_set.discard(person)

        return person_set

    def get_recipients_email(self):
        return set(map(lambda x: x.email, self.recipients))

    def clean_fields(self, exclude=None):
        super(EmailList, self).clean_fields(exclude=exclude)
        if 'forward_to' not in exclude and self.forward_to == self:
            raise ValidationError({'forward_to': 'Kan inte vidarebefordra en lista till sig själv'})

class AssociationMembership(models.Model):
    person = models.ForeignKey(Person, models.CASCADE, verbose_name='person', related_name='association_memberships')
    year = models.ForeignKey(AssociationYear, models.CASCADE, verbose_name='verksamhetsår', related_name='memberships')

    def __str__(self):
        return '{} var medlem {}'.format(self.person, self.year)
    
    class Meta:
        verbose_name = 'föreningsmedlemskap'
        verbose_name_plural = 'föreningsmedlemskap'
        
        unique_together = ['person', 'year']
        ordering = ['person', 'year']
