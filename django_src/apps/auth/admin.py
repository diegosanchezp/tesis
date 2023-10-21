from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class MyUserAdmin(UserAdmin):
    def get_fieldsets(self, request, obj=None):
        """
        Extend the get_fieldsets method to add fields
        """

        fieldsets = super().get_fieldsets(request, obj)
        personal_info_field = fieldsets[1]
        new_personal_info = (
            # keep the original name
            personal_info_field[0],
            # field_options
            {
                'fields': personal_info_field[1]["fields"] + ("profile_pic",)
            }
        )

        extended_field_sets = (
            fieldsets[0],
            new_personal_info,
            fieldsets[2],
            fieldsets[3],
        )
        return extended_field_sets


# Register the extended ModelAdmin
admin.site.register(User, MyUserAdmin)
