from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings
import random

from faker import Faker

from yourapp.factories import AuthorFactory, BookFactory


class Command(BaseCommand):
    help = "Fyller databasen med fabriksgenererad data (factory_boy)."

    def add_arguments(self, parser):
        parser.add_argument("--authors", type=int, default=10)
        parser.add_argument("--books", type=int, default=50)
        parser.add_argument("--seed", type=int, default=None)
        parser.add_argument(
            "--force", action="store_true", help="Kör även om DEBUG=False"
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        if not settings.DEBUG and not opts["force"]:
            raise CommandError("Kör inte utan --force när DEBUG=False")

        seed_value = opts["seed"]
        if seed_value:
            random.seed(seed_value)
            Faker.seed(seed_value)

        self.stdout.write(self.style.NOTICE(f"Skapar {opts['authors']} författare..."))
        authors = [AuthorFactory() for _ in range(opts["authors"])]

        self.stdout.write(self.style.NOTICE(f"Skapar {opts['books']} böcker..."))
        for _ in range(opts["books"]):
            BookFactory(author=random.choice(authors))

        self.stdout.write(self.style.SUCCESS("Seed-data skapad!"))
