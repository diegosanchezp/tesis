from django import forms
from django_src.business.register.forms import BusinessForm


class EditBusinessForm(BusinessForm):

    def __init__(self, *args, **kwargs):
        # Skip the alpine thing by using the super() method of BusinessForm
        forms.ModelForm.__init__(self, *args, **kwargs)

    field_order = ["web_page", "description"]
