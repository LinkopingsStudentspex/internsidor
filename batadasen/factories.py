from factory import Faker, django

from batadasen import models

Faker._DEFAULT_LOCALE = "sv_SE"


class ProductionFactory(django.DjangoModelFactory):
    class Meta:
        model = models.Production

    number = Faker("number")
    main_title = Faker("sentence", nb_words=3)
    subtitle = models.CharField("undertitel", max_length=100, blank=True)
    short_name = models.CharField("kort namn", max_length=50, blank=True)
    year = models.PositiveIntegerField("år", validators=[])
    plot = models.TextField("handling", max_length=1000, blank=True)
    closed = models.BooleanField("avslutad", default=False)
    regular = models.BooleanField("ordinarie", default=True)
    autumn = models.BooleanField("höstspex", default=False)
