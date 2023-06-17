import Milter
import time
import sys
import re
import os
import django
from django.db.models import Q

import subprocess

connection_string = sys.argv[1]
mail_domain = sys.argv[2]

prod_list_patt = re.compile(r'^(spex|jubel)[0-9][0-9].*@' + mail_domain)
mass_list_patt = re.compile(r'^(spexinfo|spex-info|blandat|trams)@' + mail_domain)
summons_list_patt = re.compile(r'kallelse@' + mail_domain)
display_name_patt = re.compile(r'^\s*(?P<display_name>[^<]+)<(?P<addr>\S+)>')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'internsidor.settings.production')
django.setup()

from batadasen import models

class LissMilter(Milter.Base):
    def __init__(self):  # A new instance with each new connection.
        self.id = Milter.uniqueID()  # Integer incremented with each call.

    @Milter.noreply
    def envfrom(self, mail_from, *params):
        self.envelope_from = mail_from.lstrip("<").rstrip(">")
        self.from_params = params
        self.alias = ''
        self.change_subject = False
        self.subject = ''
        self.display_name = ''
        self.header_from_addr = ''
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

        has_this_email = Q(email__iexact=self.envelope_from) | Q(address_list_email__iexact=self.envelope_from) | Q(extra_email__email__iexact=self.envelope_from)

        if protected_list and not models.Person.objects.filter(has_this_email).exists():
            valid_sender = False

        if extra_protected_list:
            current_assoc_year = models.get_current_assoc_year()
            try:
                has_this_email = Q(person__email__iexact=self.envelope_from) | Q(person__address_list_email__iexact=self.envelope_from) | Q(person__extra_email__email__iexact=self.envelope_from)
                if not current_assoc_year.groups.get(Q(group_type__short_name='STYR')).activities.filter(has_this_email).exists():
                    valid_sender = False
            except models.AssociationGroup.DoesNotExist:
                # Should only happen if no AssociationGroup called 'STYR' has been created yet
                pass

        # Check if sender is valid before discarding @studentspex.se addresses. A user sending 'from' @studentspex.se addresses should add this as an extra email in the database.
        if not valid_sender:
            if '@studentspex.se' in self.envelope_from:
                # https://pymilter.org/pymilter/namespacemilter.html#a4c8bad190cb7f54cea87f1182732ce83
                subprocess.run(f"logger --tag lissmilter Invalid sender for this address. From: {self.envelope_from} to {to}. Message discarded instead of being sent to studentspex mail list.", shell = True)
                return Milter.DISCARD
            else:
                subprocess.run(f"logger --tag lissmilter Invalid sender for this address. From: {self.envelope_from} to {to}", shell = True)
                self.setreply('554', '5.7.2', 'Sender <{}> not authorized for recipient ("{}"). Kontakta en ansvarig om du tycker det borde funka.'.format(self.envelope_from, to))
                return Milter.REJECT

        self.change_subject = is_production_list or is_mass_list or is_summons_list

        return Milter.CONTINUE

    @Milter.noreply
    def header(self, name, hval):
        if name.lower() == 'subject':
            self.subject = hval
        if name.lower() == 'from':
            name_match = display_name_patt.match(hval)
            if name_match:
                self.display_name = name_match.group('display_name').strip()
                self.header_from_addr = name_match.group('addr').strip()
            else:
                self.display_name = ''
                self.header_from_addr = hval
        return Milter.CONTINUE

    def eom(self):
        # We always need to change the sender address in case the sender uses SPF
        self.chgfrom('list-bounces@{}'.format(mail_domain))

        if self.change_subject:
            if self.subject != '':
                self.chgheader('Subject', 0, '[{}] {}'.format(self.alias.capitalize(), self.subject))

        # Change From and Reply-To headers to improve deliverability
        if self.display_name == '':
            new_header_from = 'donotreply@{}'.format(mail_domain)
            new_reply_to = self.header_from_addr
        else:
            new_header_from = '{} <donotreply@{}>'.format(self.display_name, mail_domain)
            new_reply_to = '{} <{}>'.format(self.display_name, self.header_from_addr)

        self.chgheader('From', 0, new_header_from)
        self.chgheader('Reply-To', 0, new_reply_to)

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
