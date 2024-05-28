from django.contrib import admin
from .models import Business
from django.utils.translation import gettext_lazy as _


# Register your models here.
@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "web_page")

    @admin.display(description=_("Nombre"))
    def name(self, obj):
        return obj.user.first_name
