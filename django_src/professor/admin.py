from django.contrib import admin
from .models import Professor

# Register your models here.

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):

    fields = ["user"]

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
