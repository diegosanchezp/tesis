from typing import Literal
from django.http.response import HttpResponse
from django.template.loader import render_to_string
from django_htmx.http import trigger_client_event


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


def close_modal(response: HttpResponse, modalTargetId: str):

    trigger_client_event(
        response=response,
        name="closeModal",
        params={"modalTargetId": modalTargetId},
    )


def open_modal(response: HttpResponse, modalTargetId: str):

    trigger_client_event(
        response=response,
        name="openModal",
        params={"modalTargetId": modalTargetId},
    )
