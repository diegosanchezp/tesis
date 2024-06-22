from typing import Literal
from django.http.response import HttpResponse
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django_htmx.http import trigger_client_event


def get_page_number(request):
    """
    Gets the page number from the request object.
    """
    page_number: str | int | None = request.GET.get("page") or request.POST.get("page")

    if page_number is None:
        page_number = 1
    elif isinstance(page_number, str):
        page_number = int(page_number)

    return page_number


def remove_index_publish_permission(page_permission_tester, user):
    """
    Removes the publish permission from a wagtail page that is considered an index.
    """

    if not getattr(page_permission_tester, "permissions", False):
        return page_permission_tester

    if (
        user.is_mentor or user.is_business
    ) and "publish" in page_permission_tester.permissions:
        page_permission_tester.permissions.remove("publish")

    return page_permission_tester


def hxSwap(
    response: HttpResponse,
    target_element_id: str,
    position: Literal[
        "innerHTML", "outerHTML", "afterbegin", "afterend", "beforebegin", "beforeend"
    ],
    text_html: str,
):
    """
    Args:
        text_html: The html to replace the target element with.
    """

    trigger_client_event(
        response=response,
        name="jsSwap",  # hx-swap
        params={
            "target_element_id": target_element_id,
            "position": position,
            "text_html": text_html,
        },
    )


from django.contrib.messages import get_messages


def renderMessagesAsToasts(request, response):
    """
    RPC to tell the WebUI to render django messages as toasts
    """

    text_html = render_to_string("components/messages.html", request=request)
    trigger_client_event(
        response,
        name="renderMessagesAsToasts",
        params=dict(
            target_element_id="toast_area", text_html=text_html, position="outerHTML"
        ),
    )
