import django
import os
import sys
import json

from django.contrib.auth import get_user_model
from django.db import transaction

input_filename = sys.argv[1]
import_type = sys.argv[2]
if len(sys.argv) > 3:
    settings = sys.argv[3]
else:
    settings = 'production'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'internsidor.settings.{}'.format(settings))
django.setup()

import batadasen
import showcounter

def non_null_or_blank(value):
    if value is None:
        return ''
    else:
        return value

def non_null_or_false(value):
    if value is None:
        return False
    else:
        return value


def import_batadasen(data):
    num_person = len(data['person'])
    current = 1
    persons = []
    for json_person in data['person']:
        print("Importing {}/{} persons".format(current, num_person))
        person, created = batadasen.models.Person.objects.get_or_create(member_number=json_person['medlemsnummer'])
        if created:
            person.first_name = json_person['fornamn']
            person.last_name = json_person['efternamn']
            person.spex_name = non_null_or_blank(json_person['spexnamn'])
            person.street_address = non_null_or_blank(json_person['gatuadress'])
            person.postal_locality = non_null_or_blank(json_person['postadress'])
            person.postal_code = non_null_or_blank(json_person['postnummer'])
            person.country = non_null_or_blank(json_person['land'])
            person.phone_home = non_null_or_blank(json_person['telhem'])
            person.phone_mobile = non_null_or_blank(json_person['telnalle'])
            person.phone_work = non_null_or_blank(json_person['telarbete'])
            person.phone_extra = non_null_or_blank(json_person['telextra'])
            person.address_list_email = non_null_or_blank(json_person['adresslistmail'])
            person.wants_spexpressen = non_null_or_false(json_person['spexpressen'])
            person.wants_blandat = non_null_or_false(json_person['blandat'])
            person.wants_spexinfo = non_null_or_false(json_person['spexinfo'])
            person.wants_trams = non_null_or_false(json_person['trams'])
            person.hundred_club = non_null_or_false(json_person['hundraklubb'])
            person.notes = non_null_or_blank(json_person['ovrigt'])
            person.deceased = non_null_or_false(json_person['avliden'])
            person.save()
            try:
                person.email = json_person['maillistmail']
                # Need to use an inner transaction here since the exception will break the closest
                # transaction if it happens.
                with transaction.atomic():
                    person.save()
            except django.db.utils.IntegrityError:
                msg = "Fel vid import from gamla batadasen: person med email {} fanns redan!".format(json_person['maillistmail'])
                print(msg)
                person.notes += msg
                person.email = None
                person.save()
        current += 1

    num_extramail = len(data['extramail'])
    current = 1

    for json_extramail in data['extramail']:
        print("Importing {}/{} extramail".format(current, num_extramail))
        person = batadasen.models.Person.objects.get(member_number=json_extramail['medlem'])
        email, created = batadasen.models.ExtraEmail.objects.get_or_create(person=person, email=json_extramail['email'])
        current += 1

    ASSOC_GROUPS = ['STYR', 'VALBERED', 'TOMTE', 'REV']
    PROD_GROUPS = [
        'STAB', 
        'LED', 
        'FEST', 
        'PRYL', 
        'DET', 
        'PR', 
        'KSP', 
        'MAN', 
        'ORK', 
        'LEIF', 
        'DOK', 
        'BALETT', 
        'SPEXPERT', 
        'REV', 
        'KOMM', 
        'KMPLT', 
        'KANKAN', 
        'KLANG', 
        'KULISS',
        'KARAKTAR', 
        'KRAMERI', 
        'KLADER', 
        'KAMERA', 
        'KALAS', 
        'SKÅDIS', 
        'KM', 
        'SYN', 
        'MELLO', 
        'MUSIK', 
        'TEKNIK'
    ]

    num_grupp = len(data['grupp'])
    current = 1
    for json_grupp in data['grupp']:
        print("Importing {}/{} group types".format(current, num_grupp))
        if json_grupp['kortnamn'] in ASSOC_GROUPS:
            group_type, created = batadasen.models.AssociationGroupType.objects.get_or_create(short_name=json_grupp['kortnamn'])
            if created:
                group_type.name = json_grupp['namn']
                group_type.priority = json_grupp['prio']
                group_type.save()

        if json_grupp['kortnamn'] in PROD_GROUPS:
            group_type, created = batadasen.models.ProductionGroupType.objects.get_or_create(short_name=json_grupp['kortnamn'])
            if created:
                group_type.name = json_grupp['namn']
                group_type.priority = json_grupp['prio']
                group_type.save()
        current += 1

    num_titel = len(data['titel'])
    current = 1
    for json_titel in data['titel']:
        print("Importing {}/{} titles".format(current, num_titel))
        title, created = batadasen.models.Title.objects.get_or_create(name=json_titel['namn'])
        if created:
            title.priority = json_titel['prio']
            title.email_alias = non_null_or_blank(json_titel['mailalias'])
            title.save()
        current += 1

    num_foreningsaktiv = len(data['foreningsaktiv'])
    current = 1
    for json_foreningsaktiv in data['foreningsaktiv']:
        print("Importing {}/{} association activities".format(current, num_foreningsaktiv))
        assoc_group_type = batadasen.models.AssociationGroupType.objects.get(short_name=json_foreningsaktiv['grupp'])
        assoc_year, created = batadasen.models.AssociationYear.objects.get_or_create(end_year=json_foreningsaktiv['ar'])
        assoc_group, created = batadasen.models.AssociationGroup.objects.get_or_create(year=assoc_year, group_type=assoc_group_type)
        person = batadasen.models.Person.objects.get(member_number=json_foreningsaktiv['medlem'])
        activity, created = batadasen.models.AssociationActivity.objects.get_or_create(person=person, group=assoc_group)
        if created:
            if json_foreningsaktiv['titel'] is not None:
                title = batadasen.models.Title.objects.get(name=json_foreningsaktiv['titel'])
                activity.title = title
            if json_foreningsaktiv['tillochmed'] is not None:
                activity.to_date = django.utils.dateparse.parse_date(json_foreningsaktiv['tillochmed'])
            activity.save()
        else:
            print("Already created association activity for person {}, group {}".format(person, assoc_group))
        current += 1

    num_uppsattning = len(data['uppsattning'])
    current = 1
    for json_uppsattning in data['uppsattning']:
        print("Importing {}/{} productions".format(current, num_uppsattning))
        production, created = batadasen.models.Production.objects.get_or_create(number=json_uppsattning['nr'], main_title=json_uppsattning['namn'], year=json_uppsattning['ar'])
        if created:
            production.subtitle = non_null_or_blank(json_uppsattning['undertitel'])
            production.short_name = non_null_or_blank(json_uppsattning['kortnamn'])
            production.plot = non_null_or_blank(json_uppsattning['handling'])
            production.closed = non_null_or_false(json_uppsattning['avslutad'])
            production.regular = non_null_or_false(json_uppsattning['ordinarie'])
            production.autumn = non_null_or_false(json_uppsattning['hostspex'])
            production.save()
        current += 1

    playing_dict = dict()
    for json_spelar in data['spelar']:
        playing_dict[(json_spelar['medlem'], json_spelar['uppsattning'])] = json_spelar['instrument']

    num_gruppstatus = len(data['gruppstatus'])
    current = 1
    for json_gruppstatus in data['gruppstatus']:
        print("Importing {}/{} production memberships".format(current, num_gruppstatus))
        person = batadasen.models.Person.objects.get(member_number=json_gruppstatus['medlem'])
        try:
            # Need to use an inner transaction here since the exception will break the closest
            # transaction if it happens.
            with transaction.atomic():
                title = batadasen.models.Title.objects.get(name=json_gruppstatus['titel'])
        except batadasen.models.Title.DoesNotExist:
            title = None

        production = batadasen.models.Production.objects.get(number=json_gruppstatus['uppsattning'])
        group_type = batadasen.models.ProductionGroupType.objects.get(short_name=json_gruppstatus['grupp'])
        prod_group, created_group = batadasen.models.ProductionGroup.objects.get_or_create(production=production, group_type=group_type)
        production_membership, created_membership = batadasen.models.ProductionMembership.objects.get_or_create(person=person, group=prod_group, title=title)

        if created_membership and json_gruppstatus['grupp'] == 'ORK':
            instrument = playing_dict.get((person.member_number, json_gruppstatus['uppsattning']))
            if instrument is not None:
                production_membership.comment = instrument
                production_membership.save()
        current += 1

    num_medlemskap = len(data['medlemskap'])
    current = 1
    for json_medlemskap in data['medlemskap']:
        print("Importing {}/{} association memberships".format(current, num_medlemskap))
        person = batadasen.models.Person.objects.get(member_number=json_medlemskap['medlem'])
        assoc_year, created = batadasen.models.AssociationYear.objects.get_or_create(end_year=json_medlemskap['ar'])
    
        if json_medlemskap['medlemstyp'] == 'Hedersmedlem':
            membership_type = batadasen.models.AssociationMembership.MembershipType.HONORARY
        elif json_medlemskap['medlemstyp'] == 'Livstidsmedlem':
            membership_type = batadasen.models.AssociationMembership.MembershipType.LIFETIME
        else:
            membership_type = batadasen.models.AssociationMembership.MembershipType.STANDARD
    
        membership, created = batadasen.models.AssociationMembership.objects.get_or_create(person=person, year=assoc_year, membership_type=membership_type)
        current += 1

    num_mejllistor = len(data['mejllistor'])
    current = 1
    for json_mejllistor in data['mejllistor']:
        print("Importing {}/{} mail lists".format(current, num_mejllistor))
        maillist, created = batadasen.models.EmailList.objects.get_or_create(alias=json_mejllistor['alias'])
        if json_mejllistor['uppsattning'] is not None:
            production = batadasen.models.Production.objects.get(number=json_mejllistor['uppsattning'])
        else:
            production = None

        if json_mejllistor['grupp'] is not None and json_mejllistor['grupp'].strip() != '':
            group_type, created = batadasen.models.ProductionGroupType.objects.get_or_create(short_name=json_mejllistor['grupp'])
            if created:
                print("Created new productiongrouptype with short name {}".format(json_mejllistor['grupp']))
            if production is not None:
                prod_group, created_group = batadasen.models.ProductionGroup.objects.get_or_create(production=production, group_type=group_type)
            else:
                prod_group = None
        else:
            group_type = None

        if json_mejllistor['extramedlem'] is not None:
            extra_person = batadasen.models.Person.objects.get(member_number=json_mejllistor['extramedlem'])
        else:
            extra_person = None

        if json_mejllistor['optout'] is not None:
            optout_person = batadasen.models.Person.objects.get(member_number=json_mejllistor['optout'])
        else:
            optout_person = None

        if optout_person is not None:
            maillist.opt_out_members.add(optout_person)
        elif extra_person is not None:
            maillist.opt_in_members.add(extra_person)
        else:
            # Only include entire groups if the row didn't contain an extra member or opt out
            if production is None:
                if group_type is not None:
                    maillist.all_groups.add(group_type)
            else:
                if group_type is not None:
                    maillist.production_groups.add(prod_group)
                else:
                    maillist.productions.add(production)

        maillist.save()
        current += 1

    num_password = len(data['password'])
    current = 1
    for json_password in data['password']:
        print("Importing {}/{} users".format(current, num_password))
        if json_password['username'] is not None:
            user, created = get_user_model().objects.get_or_create(username=json_password['username'])
            if created:
                person = batadasen.models.Person.objects.get(member_number=json_password['medlem'])
                person.user = user
                person.save()
        current += 1

def import_showcounter(data):
    num_teater = len(data['teater'])
    current = 1
    for json_teater in data['teater']:
        print("Importing {}/{} theatres".format(current, num_teater))
        theatre, created = showcounter.models.Theatre.objects.get_or_create(id=json_teater['id'])
        theatre.name = non_null_or_blank(json_teater['namn'])
        theatre.city = non_null_or_blank(json_teater['stad'])
        theatre.notes = non_null_or_blank(json_teater['anteckning'])
        theatre.save()
        current += 1

    num_forestallning = len(data['forestallning'])
    current = 1
    for json_forestallning in data['forestallning']:
        print("Importing {}/{} performances".format(current, num_forestallning))
        try: 
            performance = showcounter.models.Performance.objects.get(number=json_forestallning['nummer'])
        except showcounter.models.Performance.DoesNotExist:
            performance = showcounter.models.Performance(number=json_forestallning['nummer'])

        performance.date = json_forestallning['datum']
        performance.start_time = json_forestallning['tid']
        performance.notes = non_null_or_blank(json_forestallning['ovrigt'])
        performance.production = batadasen.models.Production.objects.get(number=json_forestallning['uppsattning'])
        performance.theatre = showcounter.models.Theatre.objects.get(id=json_forestallning['teater'])
        performance.tag = non_null_or_blank(json_forestallning['tag'])
        performance.save()
        current += 1

    num_forestraknare = len(data['forestraknare'])
    current = 1
    for json_forestraknare in data['forestraknare']:
        print("Importing {}/{} participations".format(current, num_forestraknare))
        person = batadasen.models.Person.objects.get(member_number=json_forestraknare['medlem'])
        performance = showcounter.models.Performance.objects.get(number=json_forestraknare['forest'])
        showcounter.models.Participation.objects.get_or_create(person=person, performance=performance)
        current += 1


with open(input_filename) as json_file:
    with transaction.atomic():
        data = json.load(json_file)

        if import_type == 'batadasen':
            import_batadasen(data)
        elif import_type == 'showcounter':
            import_showcounter(data)