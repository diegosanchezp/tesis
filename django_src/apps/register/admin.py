from django.contrib import admin

from .models import (
    Faculty,
    Carreer,
    CarrerSpecialization,
    InterestTheme,
)

# Register your models here.

@admin.register(InterestTheme)
class InterestThemeAdmin(admin.ModelAdmin):
    pass

class CarreerInline(admin.StackedInline):
    model = Carreer
    extra = 1

class CarrerSpecializationInline(admin.StackedInline):
    model = CarrerSpecialization
    extra = 1

@admin.register(Carreer)
class CarreerAdmin(admin.ModelAdmin):
    list_display = ("name",)
    inlines = [
        CarrerSpecializationInline
    ]

@admin.register(CarrerSpecialization)
class CarrerSpecializationAdmin(admin.ModelAdmin):
    pass

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    inlines = [
        CarreerInline
    ]


