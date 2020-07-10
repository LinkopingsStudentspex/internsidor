import Milter
import time
import sys
import re
import os
import django
from django.db.models import Q
from Milter.utils import parse_addr

connection_string = sys.argv[1]
mail_domain = sys.argv[2]

prod_list_patt = re.compile(r'^(spex|jubel)[0-9][0-9].*@' + mail_domain)
mass_list_patt = re.compile(r'^(spexinfo|spex-info|blandat|trams)@' + mail_domain)
summons_list_patt = re.compile(r'kallelse@' + mail_domain)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'internsidor.settings.production')
django.setup()

from batadasen import models

class LissMilter(Milter.Base):
    def __init__(self):  # A new instance with each new connection.
        self.id = Milter.uniqueID()  # Integer incremented with each call.

    @Milter.noreply
    def envfrom(self, mail_from, *params):
        self.from_addr = mail_from.lstrip("<").rstrip(">")
        self.from_params = params
        self.alias = ''
        self.change_header = False
        self.subject = ''
        return Milter.CONTINUE

    def envrcpt(self, mail_to, *str):
        to = mail_to.lstrip("<").rstrip(">")

        is_production_list = prod_list_patt.match(to) is not None
        is_mass_list = mass_list_patt.match(to) is not None
        is_summons_list = summons_list_patt.match(to) is not None

        # Use the first recipient as tag for later header modification
        if self.alias == '':
            parts = to.split('@')
            if len(parts) != 2:
                return Milter.REJECT
            self.alias = parts[0]

        protected_list = False

        try:
            email_list = models.EmailList.objects.get(alias=self.alias)
            protected_list = email_list.is_internal
        except models.EmailList.DoesNotExist:
            pass

        extra_protected_list = is_summons_list

        valid_sender = True

        has_this_email = Q(email=self.from_addr) | Q(address_list_email=self.from_addr) | Q(extra_email__email=self.from_addr)

        if protected_list and not models.Person.objects.filter(has_this_email).exists():
            valid_sender = False

        if extra_protected_list:
            current_assoc_year = models.get_current_assoc_year()
            try:
                has_this_email = Q(person__email=self.from_addr) | Q(person__address_list_email=self.from_addr) | Q(person__extra_email__email=self.from_addr)
                if not current_assoc_year.groups.get(Q(group_type__short_name='STYR')).activities.filter(has_this_email).exists():
                    valid_sender = False
            except models.AssociationGroup.DoesNotExist:
                # Should only happen if no AssociationGroup called 'STYR' has been created yet
                pass

        if not valid_sender:
            self.setreply('554', '5.7.2', 'Sender <{}> not authorized for recipient ("{}"). Kontakta en ansvarig om du tycker det borde funka.'.format(self.from_addr, to))
            return Milter.REJECT

        self.change_header = is_production_list or is_mass_list or is_summons_list

        return Milter.CONTINUE

    @Milter.noreply
    def header(self, name, hval):
        if name.lower() == 'subject':
            self.subject = hval
        return Milter.CONTINUE

    def eom(self):
        if self.change_header:
            if self.subject != '':
                self.chgheader('Subject', 0, '[{}] {}'.format(self.alias.capitalize(), self.subject))
        return Milter.CONTINUE


def main():
    timeout = 600
    Milter.factory = LissMilter

    # Tell Sendmail which features we use
    flags = Milter.CHGHDRS
    Milter.set_flags(flags)       

    print("%s milter startup" % time.strftime('%Y-%m-%d %H:%M:%S'))
    sys.stdout.flush()
    Milter.runmilter("lissmilter", connection_string, timeout)
    print("%s milter shutdown" % time.strftime('%Y-%m-%d %H:%M:%S'))


if __name__ == "__main__":
    main()