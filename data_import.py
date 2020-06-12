import django
import os
import sys
import json

input_filename = sys.argv[1]
if len(sys.argv) > 2:
    settings = sys.argv[2]
else:
    settings = 'production'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'internsidor.settings.{}'.format(settings))
django.setup()

from batadasen import models

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

with open(input_filename) as json_file:
    data = json.load(json_file)
    for json_person in data['person']:
        person, created = models.Person.objects.get_or_create(member_number=json_person['medlemsnummer'])
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
            person.save()
        except django.db.utils.IntegrityError:
            msg = "Fel vid import from gamla batadasen: person med email {} fanns redan!".format(json_person['maillistmail'])
            print(msg)
            person.notes += msg
