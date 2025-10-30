from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
import datetime

User = get_user_model()


class Category(models.Model):
    name = models.CharField(_("Name"), max_length=100)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("User"),
        related_name="added_assetcategories",
    )

    def __str__(self):
        return self.name


class AssetModel(models.Model):
    manufacturer = models.CharField(_("Manufacturer"), max_length=100)
    model_name = models.CharField(_("Model name"), max_length=100)
    model_description = models.TextField(_("Model description"), blank=True)
    categories = models.ManyToManyField(
        Category, verbose_name=_("Categories"), related_name="asset_types"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("User"),
        related_name="added_assetmodels",
    )

    def __str__(self):
        return "%s - %s" % (self.manufacturer, self.model_name)


class Owner(models.Model):
    name = models.CharField(_("Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True)

    def __str__(self):
        return self.name


def get_next_asset_number():
    last_object = Asset.objects.all().order_by("number").last()
    if last_object is None:
        return 1
    return last_object.number + 1


class Asset(models.Model):
    number = models.IntegerField(
        _("Number"),
        unique=True,
        validators=[
            MinValueValidator(1),
        ],
    )

    model = models.ForeignKey(
        AssetModel, models.PROTECT, verbose_name=_("Model"), related_name="assets"
    )

    purchase_time = models.CharField(_("Purchase time"), max_length=100, blank=True)
    purchase_price = models.CharField(_("Purchase price"), max_length=100, blank=True)
    standard_location = models.CharField(
        _("Standard location"), max_length=100, blank=True
    )
    supplier = models.CharField(_("Supplier"), max_length=100, blank=True)
    description = models.TextField(_("Description"), blank=True)

    owner = models.ForeignKey(
        Owner, on_delete=models.PROTECT, verbose_name=_("Owner"), related_name="assets"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("User"),
        related_name="added_assets",
    )

    @property
    def status_readable(self):
        if self.log_entries.exists():
            latest_log_entry = self.log_entries.latest("timestamp")
            return latest_log_entry.get_new_status_display()
        else:
            return dict(LogEntry.STATUS_CHOICES)[LogEntry.STATUS_UNKNOWN]

    def __str__(self):
        return "Asset %s, %s" % (str(self.number), self.model)


class LogEntry(models.Model):
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        verbose_name=_("Asset"),
        related_name="log_entries",
    )
    timestamp = models.DateTimeField(_("Timestamp"), default=datetime.datetime.now)
    notes = models.TextField(_("Notes"))
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("User"),
        related_name="log_entries",
    )

    STATUS_OK = "OK"  # Fully functional and ready for use
    STATUS_DEGRADED = "DEG"  # Missing some functionality but still usable
    STATUS_OUT_OF_ORDER = "OOO"  # Broken or in need of repair
    STATUS_HISTORICAL = "HIST"  # Sold, thrashed, passed on, an ex-asset...
    STATUS_UNKNOWN = "UNK"  # Status is not presently known
    STATUS_CHOICES = (
        (STATUS_OK, _("OK")),
        (STATUS_DEGRADED, _("Degraded")),
        (STATUS_OUT_OF_ORDER, _("Out of order")),
        (STATUS_UNKNOWN, _("Unknown")),
        (STATUS_HISTORICAL, _("Historical")),
    )

    new_status = models.CharField(
        _("New status"), max_length=20, choices=STATUS_CHOICES
    )

    def __str__(self):
        return "%s - %s" % (self.asset.number, self.timestamp.strftime("%Y-%m-%d"))
