from django.contrib import admin
from .models import EgresadosData
from django.utils.translation import gettext_lazy as _


@admin.register(EgresadosData)
class EgresadosDataAdmin(admin.ModelAdmin):
    search_fields = ["nombre", "apellido"]
    list_display = ("nombre", "apellido", "prefijo_cedula", "cedula")
    search_help_text = _("Búsque por nombre y apellido")
    list_filter = ["prefijo_cedula", "estatus", "sexo"]
