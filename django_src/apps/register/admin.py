from django.contrib import admin

from .models import (
    Faculty,
    Carreer,
    CarrerSpecialization,
    InterestTheme,
    Student,
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


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("first_name","last_name","email",)

    @admin.display(description="email")
    def email(self,obj):
        return obj.user.email

    @admin.display(description="First name")
    def first_name(self,obj):
        return obj.user.first_name

    @admin.display(description="Last name")
    def last_name(self,obj):
        return obj.user.last_name
