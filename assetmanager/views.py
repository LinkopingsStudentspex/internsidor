from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.exceptions import PermissionDenied

from .models import Asset, AssetModel, LogEntry, Category
from .forms import LogEntryForm, AssetForm, AssetModelForm, CategoryForm

from ajax_select import register, LookupChannel


class AssetListView(LoginRequiredMixin, generic.ListView):
    model = Asset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context

    def get_queryset(self):
        if "category" in self.request.GET:
            return Asset.objects.filter(
                model__categories__name=self.request.GET.get("category")
            )
        else:
            return Asset.objects.all()


class AssetDetailView(LoginRequiredMixin, generic.DetailView):
    model = Asset
    slug_field = "number"
    slug_url_kwarg = "number"


class AssetModelDetailView(LoginRequiredMixin, generic.DetailView):
    model = AssetModel


@login_required
def new_logentry_view(request, number):
    asset_inst = get_object_or_404(Asset, number=number)

    if request.method == "POST":
        form = LogEntryForm(request.POST)

        if form.is_valid():
            logentry_inst = LogEntry(**form.cleaned_data)
            logentry_inst.asset = asset_inst
            logentry_inst.user = request.user
            logentry_inst.save()

            return HttpResponseRedirect(
                reverse(
                    "assetmanager:asset_detail", kwargs={"number": asset_inst.number}
                )
            )

    else:
        form = LogEntryForm()

        if asset_inst.log_entries.exists():
            latest_status = asset_inst.log_entries.latest("timestamp")
            form.fields["new_status"].initial = latest_status
        else:
            form.fields["new_status"].initial = LogEntry.STATUS_UNKNOWN

    return render(
        request,
        "assetmanager/logentry_form.html",
        {"form": form, "asset_inst": asset_inst},
    )


# @permission_required('assetmanager.add_asset')
@never_cache
@login_required
def new_asset_view(request):
    if request.method == "POST":
        form = AssetForm(request.POST)

        if form.is_valid():
            initial_status = form.cleaned_data.pop("initial_status")
            initial_log_entry = form.cleaned_data.pop("initial_log_entry")

            asset_inst = Asset(**form.cleaned_data)
            asset_inst.save()

            entry = LogEntry(
                asset=asset_inst, notes=initial_log_entry, new_status=initial_status
            )
            entry.save()

            return HttpResponseRedirect(
                reverse(
                    "assetmanager:asset_detail", kwargs={"number": asset_inst.number}
                )
            )
    else:
        form = AssetForm()

    return render(request, "assetmanager/asset_form.html", {"form": form})


# @permission_required('assetmanager.add_assetmodel')
@login_required
def new_assetmodel_view(request):
    if request.method == "POST":
        form = AssetModelForm(request.POST)

        if form.is_valid():
            assetmodel_inst = AssetModel()
            assetmodel_inst.manufacturer = form.cleaned_data.pop("manufacturer")
            assetmodel_inst.model_name = form.cleaned_data.pop("model_name")
            assetmodel_inst.model_description = form.cleaned_data.pop(
                "model_description"
            )
            assetmodel_inst.save()
            for cat in form.cleaned_data.pop("categories"):
                assetmodel_inst.categories.add(cat)

            assetmodel_inst.save()

            return HttpResponseRedirect(reverse("assetmanager:asset_add"))
    else:
        form = AssetModelForm()

    return render(request, "assetmanager/assetmodel_form.html", {"form": form})


# @permission_required('assetmanager.add_category')
@login_required
def new_category_view(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)

        if form.is_valid():
            category_inst = Category(**form.cleaned_data)
            category_inst.save()

            return HttpResponseRedirect(reverse("assetmanager:assetmodel_add"))
    else:
        form = CategoryForm()

    return render(request, "assetmanager/category_form.html", {"form": form})


@login_required
def search_view(request):
    if request.method == "GET":
        asset_id = request.GET.get("id")
        if Asset.objects.filter(number=asset_id).exists():
            return HttpResponseRedirect(
                reverse("assetmanager:asset_detail", args=[asset_id])
            )

        return HttpResponseRedirect(reverse("assetmanager:asset_list"))


@register("assetmodels")
class AssetModelLookup(LookupChannel):
    model = AssetModel

    def check_auth(self, request):
        if not request.user.is_authenticated:
            raise PermissionDenied

    def get_query(self, q, request):
        return AssetModel.objects.filter(
            Q(model_name__icontains=q) | Q(manufacturer__icontains=q)
        )

    def format_item_display(self, item):
        return '<span class="assetmodel">%s %s</span>' % (
            item.manufacturer,
            item.model_name,
        )


@register("categories")
class CategoryLookup(LookupChannel):
    model = Category

    def check_auth(self, request):
        if not request.user.is_authenticated:
            raise PermissionDenied

    def get_query(self, q, request):
        return Category.objects.filter(Q(name__icontains=q))

    def format_item_display(self, item):
        return '<span class="category">%s</span>' % item.name
