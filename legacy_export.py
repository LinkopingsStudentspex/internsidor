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
    output += """INSERT INTO person (medlemsnummer, fornamn, efternamn, maillistmail) 
              VALUES ({medlemsnummer}, '{fornamn}', '{efternamn}', '{maillistmail}') 
              ON CONFLICT (medlemsnummer) DO UPDATE SET 
                fornamn = '{fornamn}', 
                efternamn = '{efternamn}', 
                maillistmail = '{maillistmail}' 
              WHERE medlemsnummer = {medlemsnummer};

              """.format(
                    medlemsnummer=person.member_number,
                    fornamn=person.first_name,
                    efternamn=person.last_name,
                    maillistmail=person.email)

for production in models.Production.objects.all():
    output += """INSERT INTO uppsattning (nr, namn, kortnamn, ar) 
              VALUES ({nr}, '{namn}', '{kortnamn}' {ar}) 
              ON CONFLICT (nr) DO UPDATE SET 
                namn = '{namn}', 
                kortnamn = '{kortnamn}', 
                ar = {ar} 
              WHERE nr = {nr};

              """.format(
                  nr=production.number,
                  namn=production.main_title,
                  kortnamn=production.short_name,
                  ar=production.year)

output += 'COMMIT;'

sys.stdout.write(output)