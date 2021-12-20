from django.db import models

from batadasen.models import Production, Person


class Theatre(models.Model):
    class Meta:
        verbose_name = 'teater'
        verbose_name_plural = 'teatrar'
    
    id = models.AutoField(primary_key=True)
    name = models.CharField('namn', max_length=100)
    city = models.CharField('stad', max_length=50)
    notes = models.CharField('anteckningar', max_length=400, blank=True)

    def __str__(self):
        return self.name


class Performance(models.Model):
    class Meta:
        verbose_name = 'föreställning'
        verbose_name_plural = 'föreställningar'

    number = models.AutoField(primary_key=True, verbose_name='nummer')
    date = models.DateField('datum')
    time = models.TimeField('time', null=True, blank=True)
    notes = models.CharField(max_length=400, verbose_name='övrigt', blank=True, help_text="Allmäna övriga anmärkningar om föreställningen")
    production = models.ForeignKey(Production, on_delete=models.CASCADE, verbose_name='uppsättning', related_name='performances')
    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE, verbose_name='teater', related_name='performances')
    tag = models.CharField(verbose_name='tag', max_length=20, blank=True, help_text="Vilken typ av föreställning, t.ex. Premiär, Genrep, Extra")

    def __str__(self):
        return f"({self.number}) {self.production.main_title} - {self.date}"


class Participation(models.Model):
    class Meta:
        verbose_name = 'föreställningsdeltagande'
        verbose_name_plural = 'föreställningsdeltaganden'
        constraints = [
            models.UniqueConstraint(fields=['person', 'performance'], name='unique_participation')
        ]
    
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name='person', related_name='performances')
    performance = models.ForeignKey(Performance, on_delete=models.CASCADE, verbose_name='föreställning', related_name='participants')

    def __str__(self):
        return '{}: {}'.format(self.person, self.performance)