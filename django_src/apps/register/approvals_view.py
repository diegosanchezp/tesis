from datetime import datetime
from django.db.models.query import QuerySet
from django.db.models import Case, When, Value, IntegerField
from django.http import HttpResponse, QueryDict
from django.template.response import TemplateResponse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .forms import ApprovalsFilterForm
from .models import RegisterApprovals, RegisterApprovalEvents, RegisterApprovalStates, approval_state_machine
from django.core.paginator import Paginator

from django.template import RequestContext

from render_block import render_block_to_string


def paginate_queryset(request, queryset):

    filter_form = get_approvals_form(request)
    page_number = get_page_number(request)

    # Don't forget to change per_page to 12 when testing is done
    # 12 it's what looks best in the UI
    paginator = Paginator(object_list=queryset, per_page=12)  # Show 12 approvals per page.
    page_obj = paginator.get_page(page_number)

    # Create a QueryDict to store the search query params
    search_query_params = QueryDict(mutable=True)

    # Validate to populate cleaned_data
    filter_form.is_valid()

    for (key,value) in filter_form.cleaned_data.items():
        if (
            value  and value != '' and key not in ["action", "approvals"]
        ):
            if key == "user_type":
                search_query_params[key] = value.model
            else:
                search_query_params[key] = value

    return {
        "page_obj": page_obj,
        "page_number": page_number,
        "paginator": paginator,
        "search_query_params": search_query_params.urlencode(),
    }


def get_approvals():
    """
    Gets and sorts the approvals queryset by state
    """

    approvals = RegisterApprovals.objects.select_related("user", "user_type").order_by(
        Case(
            When(state=RegisterApprovalStates.WAITING, then=Value(0)),
            When(state=RegisterApprovalStates.APPROVED, then=Value(1)),
            When(state=RegisterApprovalStates.REJECTED, then=Value(2)),
            default=Value(3),
            output_field=IntegerField(),
        )
    )

    return approvals

def get_page_number(request):
    page_number: str | int | None = request.GET.get("page") or request.POST.get("page")

    if page_number is None:
        page_number = 1
    elif isinstance(page_number, str):
        page_number = int(page_number)

    return page_number

def get_approvals_form(request):

    return ApprovalsFilterForm(getattr(request, request.method))

def filter_approvals(approvals, status=None, name=None, user_type=None):
    if status:
        if status != "all":
            approvals = approvals.filter(state=status)
    if name:
        approvals = approvals.filter(user__first_name__icontains=name)
    if user_type:
        approvals = approvals.filter(user_type=user_type)

    return approvals

def filter_users(request):
    """
    Filters the list of students/mentors
    by name or status.

    Processed user: someone who's been approved or rejected.
    """

    approvals = get_approvals()

    filter_form = get_approvals_form(request)

    # Filter the queryset, if the filter_form is valid
    if filter_form.is_valid():
        approvals = filter_approvals(
            approvals,
            status=filter_form.cleaned_data["status"],
            name=filter_form.cleaned_data["name"],
            user_type=filter_form.cleaned_data["user_type"]
        )

    context = {
        "filter_form": filter_form,
        # Todo figure out howt to get page number when a filter is applied
        **paginate_queryset(request, approvals),
    }

    return context

def approve_reject_users(request):
    """
    Approves or rejects an user register request
    """

    filter_form = get_approvals_form(request)

    context = {
        "filter_form": filter_form,
    }

    form_valid = filter_form.is_valid()
    cleaned_data = filter_form.cleaned_data

    if (
        form_valid and "action" in cleaned_data
        and "approvals" in cleaned_data
    ):
        action = cleaned_data["action"]
        approvals: QuerySet[RegisterApprovals] = cleaned_data["approvals"]

        # Get the next state

        for approval in approvals:
            # approval_state_machine shouldn't raise any errors because it's getting validated in the form
            # if it does we don't want to continue and the client will recieve a server error (500)
            next_state = approval_state_machine[approval.state][action]
            approval.state = next_state
            approval.admin = request.user
            approval.date = datetime.now()
            approval.save()

        # If there are any approvals, add a success message
        if len(approvals) > 0:
            # Add success message
            user_names = ", ".join([f"{approval.user.first_name} {approval.user.last_name}, " for approval in approvals])
            user_str = _("usuario")
            if len(approvals) > 1:
                user_str = _("usuarios")
            messages.success(
                request,
                _("%(action)s %(user_str)s %(user_names)s") % {
                    "user_names": user_names,
                    "action": RegisterApprovalEvents[action].label,
                    "user_str": user_str,
                }
            )

    approvals = filter_approvals(
        get_approvals(),
        # I think we should ignore the status filter when approving or rejecting
        # The admin won't be able to see the approved user

        # status=filter_form.cleaned_data["status"],
        name=filter_form.cleaned_data["name"],
        user_type=filter_form.cleaned_data["user_type"]
    )
    context.update(paginate_queryset(request, approvals))
    return context

def approvals_view(request):
    """
    The main view
    """

    template_name = "register/approvals.html"

    approvals = get_approvals()

    # We are visiting the page for the first time, or asking for a filtered page
    if request.method == "GET" and not request.htmx:
        filter_form = get_approvals_form(request)

        context = {
            "filter_form": filter_form,
            "RegisterApprovalStates": RegisterApprovalStates,
            "RegisterApprovalEvents": RegisterApprovalEvents,
            **paginate_queryset(request, approvals),
        }

        return TemplateResponse(request, template_name, context)

    if request.method == "POST" and request.htmx:

        approvals_form = get_approvals_form(request)

        # Default context, was it's returned when the page was first visited
        context = {
            "filter_form": approvals_form,
            "RegisterApprovalStates": RegisterApprovalStates,
            "RegisterApprovalEvents": RegisterApprovalEvents,
            **paginate_queryset(request, approvals),
        }

        if approvals_form.is_valid():
            action = approvals_form.cleaned_data["action"]

            # We are trying to filter the list of students/mentors
            if action == "search":
                context.update(**filter_users(request))

            # We are trying to approve or reject, one or more, students or mentors
            if action in [RegisterApprovalEvents.APPROVE, RegisterApprovalEvents.REJECT]:
                context.update(**approve_reject_users(request))

        # Use request context to add the messages
        request_context = RequestContext(
            request, context
        )

        # Make a response with the filtered/updated approvals table
        form_html = render_block_to_string(template_name, "approvals_table", request_context)
        htmx_reponse = HttpResponse(form_html)

        return htmx_reponse
