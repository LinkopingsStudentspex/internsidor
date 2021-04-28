"""

Det här är en enkel TCP-server som använder Django's databasapi för att
servera lookups from Postfix av mottagarlistor för epostlistor. 

Karl Linderhed 2020-03-19

"""
import django
import os
import sys
import socketserver
import pynetstring
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'internsidor.settings.production')
django.setup()

from batadasen import models
User = django.contrib.auth.get_user_model()

# Mailgun modifies the bounce address to be like bounce+stuff-address=domain@studentspex.se
bounce_pattern = re.compile(r'^bounce\+')

def spellcorrect(alias):
    direction_match = re.match(r'^(direktion|direcktion)(?P<year>[0-9][0-9])$', alias)
    if direction_match is not None:
        return 'direction{}'.format(direction_match.group('year'))

    directionen_match = re.match(r'^(direktionen|direcktionen)$', alias)
    if directionen_match is not None:
        return 'directionen'

    directeur_match = re.match(r'^(direktor|director|direcktor)(?P<year>[0-9][0-9])$', alias)
    if directeur_match is not None:
        return 'directeur{}'.format(directeur_match.group('year'))

    biljetter_match = re.match(r'^(biljett|biletter|billetter|billjett|billjetter|bijett|bijetter)$', alias)
    if biljetter_match is not None:
        return 'biljetter'

    ordf_match = re.match(r'^(ordforanden|ordforande)$', alias)
    if ordf_match is not None:
        return 'ordf'

    redaktoren_match = re.match(r'^(red|redaktor|redaktionen)$', alias)
    if redaktoren_match is not None:
        return 'redaktoren'

    forvaltaren_match = re.match(r'^(forvaltare)$', alias)
    if forvaltaren_match is not None:
        return 'forvaltaren'

    kassoren_match = re.match(r'^(kassor)$', alias)
    if kassoren_match is not None:
        return 'kassoren'

    sekreteraren_match = re.match(r'^(sekr|sekreterare)$', alias)
    if sekreteraren_match is not None:
        return 'sekreteraren'

    vordf_match = re.match(r'^(viceordforanden|viceordforande)$', alias)
    if vordf_match is not None:
        return 'vordf'

    valberedningen_match = re.match(r'^(valberedning)$', alias)
    if valberedningen_match is not None:
        return 'valberedningen'

    return ''

class PostfixTCPHandler(socketserver.BaseRequestHandler):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

    def handle(self):
        self.data = pynetstring.decode(self.request.recv(1024))[0]
        data_parts = self.data.decode().split(' ')
        if len(data_parts) != 2:
            self.request.sendall(pynetstring.encode('PERM Invalid request'))
            return

        # We don't really care about the name of the request/lookup
        # lookup_name = parts[0]
        
        email_parts = data_parts[1].split('@')
        if len(email_parts) == 1:
            # Postfix does various lookups, not just with the to-address of the
            # received email. We'll just act like we don't know anything about them.
            self.request.sendall(pynetstring.encode('NOTFOUND '))
            return
        elif len(email_parts) != 2:
            # Either an empty key or several '@'... doesn't seem right.
            self.request.sendall(pynetstring.encode('PERM Invalid request'))
            return
        
        alias = email_parts[0]

        # If it's a bounce address, send it to the 'list-bounces' list
        if bounce_pattern.match(alias) is not None:
            alias = 'list-bounces'

        found = False

        try:
            email_list = models.EmailList.objects.get(alias=alias)
            found = True
        except models.EmailList.DoesNotExist:
            found = False

        if found == False:
            # Perhaps it's a username
            try:
                user = User.objects.get(username__iexact=alias)
                if user.person is not None and user.person.email is not None and user.person.email != '':
                    reply = 'OK {}'.format(user.person.email)
                    self.request.sendall(pynetstring.encode(reply))
                    return
                else:
                    found = False
            except User.DoesNotExist:
                found = False

        if found == False:
            # Perhaps it matches some common (and uncommon) misspellings
            try:
                email_list = models.EmailList.objects.get(alias=spellcorrect(alias))
                found = True
            except models.EmailList.DoesNotExist:
                found = False

        if found == False:
            self.request.sendall(pynetstring.encode('NOTFOUND '))
            return
        
        addresses = email_list.get_recipients_email()
        if len(addresses) == 0:
            self.request.sendall(pynetstring.encode('TEMP No recipients in list'))
            return
        
        reply = 'OK {}'.format(','.join(addresses))
        self.request.sendall(pynetstring.encode(reply))

HOST, PORT = "localhost", int(sys.argv[1])
with socketserver.TCPServer((HOST, PORT), PostfixTCPHandler) as server:
    print("Listening for postfix lookups on {}:{}".format(HOST, PORT))
    server.serve_forever()