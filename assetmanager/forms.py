from django import forms
from .models import Category, LogEntry, Asset, AssetModel, Owner, get_next_asset_number
from django.utils.translation import ugettext_lazy as _
import datetime
from django.contrib.admin import widgets

from ajax_select.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField

class CategoryForm(forms.Form):
    name = forms.CharField(label=_("Name"), max_length=100)
    name.widget.attrs['class'] = "form-control"
    
class AssetModelForm(forms.Form):
    manufacturer = forms.CharField(label=_("Manufacturer"), max_length=100)
    manufacturer.widget.attrs['class'] = "form-control"

    model_name = forms.CharField(label=_("Model name"), max_length=100)
    model_name.widget.attrs['class'] = "form-control"

    model_description = forms.CharField(label=_("Model description"), widget=forms.Textarea(attrs={'rows':2}))
    model_description.widget.attrs['class'] = "form-control"

    categories = AutoCompleteSelectMultipleField('categories', label=_("Categories") )
    categories.widget.attrs['class'] = "form-control"


class LogEntryForm(forms.Form):
    timestamp = forms.DateTimeField(label=_("Timestamp"), initial=datetime.datetime.now)
    timestamp.widget.attrs['class'] = "form-control"

    new_status = forms.ChoiceField(label=_("New status"), choices=LogEntry.STATUS_CHOICES)
    new_status.widget.attrs['class'] = "form-control"

    notes = forms.CharField(label=_("Notes"), widget=forms.Textarea)
    notes.widget.attrs['class'] = "form-control"
    

class AssetForm(forms.Form):
    number = forms.IntegerField(label=_("Number"), min_value=1, initial=get_next_asset_number)
    number.widget.attrs['class'] = "form-control"

    model = AutoCompleteSelectField('assetmodels',label=_("Model") )
    model.widget.attrs['class'] = "form-control"

    owner = forms.ModelChoiceField(label=_("Owner"), queryset=Owner.objects.all())
    owner.widget.attrs['class'] = "form-control"

    purchase_time = forms.CharField(label=_("Purchase time"), max_length=100, required=False)
    purchase_time.widget.attrs['class'] = "form-control"

    purchase_price = forms.CharField(label=_("Purchase price"), max_length=100, required=False)
    purchase_price.widget.attrs['class'] = "form-control"

    standard_location = forms.CharField(label=_("Standard location"), max_length=100, required=False)
    standard_location.widget.attrs['class'] = "form-control"

    supplier = forms.CharField(label=_("Supplier"), max_length=100, required=False)
    supplier.widget.attrs['class'] = "form-control"

    description = forms.CharField(label=_("Description"), widget=forms.Textarea(attrs={'rows':2}), required=False)
    description.widget.attrs['class'] = "form-control"

    initial_status = forms.ChoiceField(label=_("Initial status"), choices=LogEntry.STATUS_CHOICES, initial=LogEntry.STATUS_UNKNOWN)
    initial_status.widget.attrs['class'] = "form-control"

    initial_log_entry = forms.CharField(label=_("Initial log entry"), widget=forms.Textarea(attrs={'rows':2}))
    initial_log_entry.widget.attrs['class'] = "form-control"


    def clean_number(self):
        data = self.cleaned_data.get('number')
        if data is None:
            raise forms.ValidationError(_('number cannot be empty'))
        if Asset.objects.filter(number=data).exists():
            raise forms.ValidationError(_('Another asset already has this number: ') + str(data))
        
        return data


