"""
lecacy_export.py
Exports the minimum amount of data needed for old systems to keep working, as postgresql queries.
"""
import django
import os
import sys

if len(sys.argv) > 1:
    settings = sys.argv[1]
else:
    settings = 'production'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'internsidor.settings.{}'.format(settings))
django.setup()

from batadasen import models

output = 'START TRANSACTION;'

for person in models.Person.objects.all():
    email = ''
    if person.email is not None:
        email = person.email.replace('\'', '\'\'')
    output += """
              UPDATE person SET 
                fornamn='{fornamn}', 
                efternamn='{efternamn}', 
                maillistmail='{maillistmail}' 
              WHERE medlemsnummer={medlemsnummer};

              INSERT INTO person (medlemsnummer, fornamn, efternamn, maillistmail) 
              VALUES ({medlemsnummer}, '{fornamn}', '{efternamn}', '{maillistmail}') 
              WHERE NOT EXISTS (SELECT 1 FROM person WHERE medlemsnummer = {medlemsnummer});

              """.format(
                    medlemsnummer=person.member_number,
                    fornamn=person.first_name.replace('\'', '\'\''),
                    efternamn=person.last_name.replace('\'', '\'\''),
                    maillistmail=email)

for production in models.Production.objects.all():
    output += """
              UPDATE uppsattning SET
                namn='{namn}', 
                kortnamn='{kortnamn}', 
                ar={ar}
              WHERE nr={nr};
              
              INSERT INTO uppsattning (nr, namn, kortnamn, ar) 
              VALUES ({nr}, '{namn}', '{kortnamn}' {ar}) 
              WHERE NOT EXISTS (SELECT 1 FROM uppsattning WHERE nr = {nr});

              """.format(
                  nr=production.number,
                  namn=production.main_title.replace('\'', '\'\''),
                  kortnamn=production.short_name.replace('\'', '\'\''),
                  ar=production.year)

output += 'COMMIT;'

sys.stdout.write(output)