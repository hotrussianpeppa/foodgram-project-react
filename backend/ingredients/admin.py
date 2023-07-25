from import_export.admin import ImportExportModelAdmin

from django.conf import settings
from django.contrib import admin

from .models import Ingredient


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = settings.EMPTY_VALUE
