from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models.query import QuerySet
from django.http.response import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
)
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django.template.response import TemplateResponse
from render_block import render_block_to_string

from django_src.utils.webui import renderMessagesAsToasts
from django_src.apps.register.models import InterestTheme
from django_src.utils import get_page_number, formdata_to_querystring
from .forms import EditInterestThemeForm, TableFilterForm

index_template_name = "customwagtail/interest_themes/index.html"

update_form_id_prefix = "update-theme-form"
create_form_id_prefix = "create-theme-form"


def get_action(rquery):
    return rquery.get("action")


def get_interests_queryset():
    return InterestTheme.objects.order_by("name")


def paginate_interests_themes(page_number: int, interests: QuerySet | None = None):

    if interests is None:
        interests = get_interests_queryset()
    paginator = Paginator(
        object_list=interests,
        # Show 12 themes per page.
        per_page=12,
    )

    page_obj = paginator.get_page(page_number)
    return page_obj


def get_table_context(request):
    page_number = get_page_number(request)

    filter_form = TableFilterForm(data=request.GET)
    interests = get_interests_queryset()
    if filter_form.is_valid():
        interests = apply_filter(interests, name=filter_form.cleaned_data.get("name"))
    filter_queryparams = formdata_to_querystring(
        filter_form,
    )
    context = {"filter_form": filter_form, "filter_queryparams": filter_queryparams}
    context["state"] = "read"
    context["interest_themes"] = paginate_interests_themes(page_number, interests)
    return context


# Main entry point
@require_http_methods(["GET", "POST"])
def crud_interest(request):
    """ """
    template_name = index_template_name

    context = {}

    if request.method == "GET":
        context.update(
            {
                "create_interest_theme_form": EditInterestThemeForm(
                    form_id=create_form_id_prefix
                ),
            }
        )

        action = get_action(request.GET)

        if action == "get_edit_row":
            return get_edit_row(request)
        if action == "restore_row":
            return restore_row(request)
        if action == "refresh_table":
            return refresh_table(request)
        if request.htmx:
            # If htmx request and page query param is present, return only the table
            if request.GET.get("page", False):
                return refresh_table(request)

        # No action return whole page
        table_context = get_table_context(request)
        context.update(table_context)
        return TemplateResponse(request, template_name, context)

    if request.method == "POST":
        if (action := get_action(request.POST)) is None:
            return HttpResponseBadRequest("Action not found")
        if action == "create_interest_theme":
            return create_interest_theme(request)
        elif action == "update_interest_theme":
            return update_interest_theme(request)
        elif action == "delete_interest_theme":
            return delete_interest_theme(request)
        else:
            return HttpResponseNotFound(f"Action {action} not handled")

    return HttpResponseBadRequest("Method not allowed")


def apply_filter(queryset, name: str | None = None):
    if name:
        queryset = queryset.filter(name__icontains=name)
    return queryset


@require_GET
def refresh_table(request):
    table_html = get_table_html(request)
    return HttpResponse(table_html)


@require_POST
def create_interest_theme(request):
    interest_t_form = EditInterestThemeForm(
        form_id=create_form_id_prefix, data=request.POST
    )
    if interest_t_form.is_valid():
        interest_t_form.save()
        # Render the whole table & a new empty form
        context = get_table_context(request)
        context["create_interest_theme_form"] = EditInterestThemeForm(
            form_id=create_form_id_prefix
        )
        messages.add_message(request, messages.SUCCESS, "Tema de interés creado")
        messages.add_message(
            request,
            messages.INFO,
            "Si no encuentras el nuevo tema creado en la tabla, buscalo por nombre",
        )
        html = render_block_to_string(
            template_name=index_template_name,
            block_name="table_and_form",
            context=context,
        )
        response = HttpResponse(html)
        renderMessagesAsToasts(request, response)
        return response

    # Render only the form with errors
    context = {"create_interest_theme_form": interest_t_form}
    html = render_block_to_string(
        template_name=index_template_name,
        block_name="create_theme_form",
        context=context,
    )
    response = HttpResponseBadRequest(html)
    return response


def get_row_html(state, interest_theme, form=None):
    html = render_block_to_string(
        template_name=index_template_name,
        block_name="theme_row",
        context={"state": state, "theme": interest_theme, "form": form},
    )
    return html


def interest_not_found_response(request):
    messages.error(request, "Tema de interés no encontrado")
    response = HttpResponseNotFound("Interest theme not found")
    renderMessagesAsToasts(request, response)
    return response


def get_interest_or_err(request_query):
    try:
        interest_theme = InterestTheme.objects.get(pk=request_query.get("id"))
        return interest_theme
    except InterestTheme.DoesNotExist:
        return None


def get_restore_row_html(interest_theme):
    return get_row_html(state="read", interest_theme=interest_theme)  # previous state


@require_GET
def restore_row(request):
    if (interest_theme := get_interest_or_err(request.GET)) is None:
        return interest_not_found_response(request)

    html = get_restore_row_html(interest_theme)
    response = HttpResponse(html)
    return response


def get_edit_row(request):
    if (interest_theme := get_interest_or_err(request.GET)) is None:
        return interest_not_found_response(request)

    form = EditInterestThemeForm(form_id=update_form_id_prefix, instance=interest_theme)

    html = get_row_html(state="update", interest_theme=interest_theme, form=form)
    response = HttpResponse(html)

    return response


@require_POST
def update_interest_theme(request):
    if (interest_theme := get_interest_or_err(request.POST)) is None:
        return interest_not_found_response(request)

    interest_t_form = EditInterestThemeForm(
        form_id=update_form_id_prefix, instance=interest_theme, data=request.POST
    )
    if interest_t_form.is_valid():
        interest_theme = interest_t_form.save()
        html = get_restore_row_html(interest_theme)
        response = HttpResponse(html)
        messages.success(request, "Tema de interés actualizado")
        renderMessagesAsToasts(request, response)
        return response

    html = get_row_html(
        state="update", interest_theme=interest_theme, form=interest_t_form
    )
    response = HttpResponse(html)
    return response


def get_table_html(request):
    context = get_table_context(request)
    html = render_block_to_string(
        template_name=index_template_name, block_name="theme_table", context=context
    )
    return html


@require_POST
def delete_interest_theme(request):

    if (interest_theme := get_interest_or_err(request.POST)) is None:
        return interest_not_found_response(request)

    interest_theme.delete()

    html = get_table_html(request)
    response = HttpResponse(html)
    messages.success(request, f"Tema {interest_theme.name} eliminado")
    renderMessagesAsToasts(request, response)

    return response
