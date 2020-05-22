from django.core.management.base import BaseCommand, CommandError
from rest_framework_api_key.models import APIKey

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('name', type=str)
        parser.add_argument('-f', action='store_true')

    def handle(self, *args, **options):
        existing_objects = APIKey.objects.filter(name=options['name'])
        already_exists = existing_objects.exists()
        if already_exists:
            if options['f']:
                existing_objects.delete()
            else:
                return
        api_key, key = APIKey.objects.create_key(name=options['name'])
        print(key)
