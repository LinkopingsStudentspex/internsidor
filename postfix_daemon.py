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

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'internsidor.settings.production')
django.setup()

from batadasen import models

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

        try:
            email_list = models.EmailList.objects.get(alias=alias)
        except models.EmailList.DoesNotExist:
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