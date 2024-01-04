from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class MyUserAdmin(UserAdmin):

    def get_fieldsets(self, request, obj=None):
        """
        Extend the get_fieldsets method to add fields to the edit/add form
        in the django admin UI

        https://docs.djangoproject.com/en/stable/ref/contrib/admin/#django.contrib.admin.ModelAdmin.fieldsets
        """

        fieldsets = super().get_fieldsets(request, obj)

        extended_fieldsets = (
            fieldsets[0],
            (
                "Personal info",
                {
                    "fields": ("first_name", "last_name", 'profile_pic', "email"),
                }
            )
        )
        return extended_fieldsets


# Register the extended ModelAdmin
admin.site.register(User, MyUserAdmin)
