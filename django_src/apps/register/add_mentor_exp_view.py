import json
from django.http.request import QueryDict

from django.urls.base import reverse_lazy

from .forms import  get_MentorExperienceFormSet
from .views import step_urls

from django.http import HttpResponse

from django.template.response import TemplateResponse

from render_block import render_block_to_string

from django_htmx.http import trigger_client_event

# just a namespace for the actions
actions = {
    "validate_add_form": "validate_add_form",
    "validate": "validate",
}

def strip_clean_data(cleaned_data: dict):
    """
    Remove unwanted fields from cleaned data
    """
    return {
        k:v for k,v in cleaned_data.items()
        if k not in ["id"]
    }

def get_POST_context_data(request):

    MentorExperienceFormSet = get_MentorExperienceFormSet()
    context = {
        "formset": MentorExperienceFormSet(data=request.POST),
        "action": request.POST.get("action"),
    }

    action = context["action"]

    old_formset = context["formset"]

    if old_formset.is_valid():
        # Remove the old formset from the context

        context.pop("formset")

        # create a new formset with the TOTAL_FORMS incremented by 1, this adds
        # a new empty form to the set
        form_data = request.POST.dict()
        total_form_key = f"{old_formset.prefix}-TOTAL_FORMS"

        if action == "validate_add_form":
            form_data[total_form_key] = int(form_data[total_form_key]) + 1

        # Add the new formset to the context
        context["formset"] = MentorExperienceFormSet(data=form_data)

    return context

def get_GET_context_data(request):

    action = request.GET.get("action")


    if request.htmx and action == "get_form_localstorage":

        initial = json.loads(request.GET["mentor_exp"])

        # The formset extra and max_num have to match
        # otherwise another forms in initial might be missing

        MentorExperienceFormSet = get_MentorExperienceFormSet(
            extra=len(initial),
            max_num=len(initial),
        )

        formset = MentorExperienceFormSet(initial=initial)

        return {
            "formset": formset,
        }


    # Craft an empty formset
    MentorExperienceFormSet = get_MentorExperienceFormSet()

    return {
        "step_urls": step_urls,
        "formset": MentorExperienceFormSet()
    }


def add_mentor_exp_view(request):
    template_name = 'register/add_mentor_exp.html'

    formset_block_name = "formset"

    action = request.POST.get("action")
    print(action)

    if request.method == "POST" and request.htmx:

        context = get_POST_context_data(request)

        form_html = render_block_to_string(template_name, formset_block_name, context)

        # Make a response with the rendered new list of themes
        htmx_reponse = HttpResponse(form_html)

        formset = context["formset"]

        # Trigger a client event to let the client know that the formset has been
        # processed an validated

        query_next_url = QueryDict(mutable=True)

        query_next_url["profile"] = request.POST.get("profile")
        query_next_url["carreer"] = request.POST.get("carreer")


        event_data = {
            # "form_dict": formset.data,
            "action": action,
            "next_url": f"{reverse_lazy('register:complete_profile')}?{query_next_url.urlencode()}",
            "form_valid": formset.is_valid() and all(
                [len(data) > 0 for data in formset.cleaned_data]
            ),
        }

        if formset.is_valid():

            # Filter out the empty forms from the cleaned data
            cleaned_data = list(
                filter(lambda x: len(x) > 0, formset.cleaned_data)
            )

            # Exclude id field and others, ...
            event_data["cleaned_data"] = list(
                map(strip_clean_data,cleaned_data)
            )

        else:
            # Collect the valid data from valid sub forms
            cleaned_data = []

            for form in formset:
                if form.is_valid():
                    cleaned_data.append(
                        strip_clean_data(form.cleaned_data)
                    )
            event_data["cleaned_data"] = cleaned_data

        trigger_client_event(
            response=htmx_reponse,
            name="formset_validated",
            params=event_data,
        )

        return htmx_reponse


    if request.method == "GET":
        context = get_GET_context_data(request)

        # We are visiting the page back again
        if request.htmx:
            form_html = render_block_to_string(template_name, formset_block_name, context)
            htmx_reponse = HttpResponse(form_html)
            return htmx_reponse
        return TemplateResponse(request, template_name, context)


        # Make a response with the rendered new list of themes
