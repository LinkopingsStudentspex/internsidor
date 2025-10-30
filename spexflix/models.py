from django.db import models
from django.core.validators import FileExtensionValidator
import os

UPLOAD_PREFIX = "spexflix"


def get_video_upload_path(instance, filename):
    if instance.production is None:
        path = os.path.join(UPLOAD_PREFIX, "misc", filename)
    else:
        path = os.path.join(UPLOAD_PREFIX, instance.production.short_name, filename)

    return instance.video_file.storage.get_available_name(path)


def get_subtitle_upload_path(instance, filename):
    if instance.video.production is None:
        path = os.path.join(UPLOAD_PREFIX, "misc", filename)
    else:
        path = os.path.join(
            UPLOAD_PREFIX, instance.video.production.short_name, "subtitles", filename
        )

    return instance.subtitle_file.storage.get_available_name(path)


def get_poster_upload_path(instance, filename):
    return instance.poster_image.storage.get_available_name(
        os.path.join(UPLOAD_PREFIX, instance.short_name, filename)
    )


class VideoType(models.TextChoices):
    SHOW = "SHOW", "Föreställning"
    EXTRA = "EXTRA", "Extramaterial"
    OTHER = "OTHER", "Övrigt"


class Production(models.Model):
    short_name = models.CharField(
        max_length=10,
        verbose_name="Kortnamn",
        help_text="T.ex Spex-19, men kan också vara något annat som identifierar en speciell uppsättning (t.ex SM-17 eller Jubel-35)",
    )
    year = models.PositiveSmallIntegerField(verbose_name="År")
    title = models.CharField(max_length=200, verbose_name="Titel")
    subtitle = models.CharField(max_length=200, verbose_name="Undertitel", blank=True)
    poster_image = models.ImageField(
        null=True,
        blank=True,
        verbose_name="Omslagsbild",
        upload_to=get_poster_upload_path,
    )
    information = models.TextField(
        max_length=2000,
        blank=True,
        verbose_name="Information",
        help_text="Beskriv spexets handling eller annat som kan vara intressant.",
    )

    class Meta:
        verbose_name = "Uppsättning"
        verbose_name_plural = "Uppsättningar"
        ordering = ["-year"]

    def __str__(self):
        return "{} - {}".format(self.short_name, self.title)

    @property
    def main_show(self):
        return self.videos.filter(video_type=VideoType.SHOW).first()


class Video(models.Model):
    title = models.CharField(
        verbose_name="Videotitel",
        max_length=200,
        help_text='Vad är detta för video? Typiskt "Föreställning" eller "Spexialmaterial" eller liknande',
    )
    video_file = models.FileField(
        verbose_name="Fil",
        upload_to=get_video_upload_path,
        validators=[FileExtensionValidator(["mp4", "m4v"])],
    )
    information = models.TextField(
        verbose_name="Information",
        max_length=500,
        blank=True,
        help_text="Ytterligare information om videon, t.ex inspelningsdatum, plats eller vem som har gjort klipping etc",
    )
    production = models.ForeignKey(
        Production,
        models.SET_NULL,
        verbose_name="Uppsättning",
        null=True,
        blank=True,
        related_name="videos",
    )

    video_type = models.CharField(
        max_length=10,
        verbose_name="Videotyp",
        choices=VideoType.choices,
        default=VideoType.SHOW,
    )

    class Meta:
        verbose_name = "Video"
        verbose_name_plural = "Videos"

    def __str__(self):
        if self.production is None:
            return "{} ({})".format(self.title, self.video_file.name)
        else:
            return "{} - {}".format(self.production.short_name, self.title)


class SubtitleTrack(models.Model):
    name = models.CharField(verbose_name="Namn", max_length=20)
    subtitle_file = models.FileField(
        verbose_name="Fil",
        upload_to=get_subtitle_upload_path,
        validators=[FileExtensionValidator(["vtt"])],
    )
    video = models.ForeignKey(
        Video, models.CASCADE, verbose_name="Video", related_name="subtitles"
    )

    class Meta:
        verbose_name = "Undertextspår"
        verbose_name_plural = "Undertextspår"

    def __str__(self):
        return "{} - {}".format(self.video, self.name)
