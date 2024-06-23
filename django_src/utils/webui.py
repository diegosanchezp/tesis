from typing import Literal
from django.http.response import HttpResponse
from django.template.loader import render_to_string
from django_htmx.http import trigger_client_event


class HXSwap:
    """
    Multiple hx-swap
    """

    def __init__(self, response: HttpResponse):
        self.response = response
        self.swaps = []
        self.triggered = False

    def swap(
        self,
        target_element_id: str,
        position: Literal[
            "innerHTML",
            "outerHTML",
            "afterbegin",
            "afterend",
            "beforebegin",
            "beforeend",
        ],
        text_html: str,
    ):
        """
        Args:
            text_html: The html to replace the target element with.
        """

        self.swaps.append(
            {
                "target_element_id": target_element_id,
                "position": position,
                "text_html": text_html,
            }
        )
        # Allow chaining
        return self

    def singleSwap(
        self,
        target_element_id: str,
        position: Literal[
            "innerHTML",
            "outerHTML",
            "afterbegin",
            "afterend",
            "beforebegin",
            "beforeend",
        ],
        text_html: str,
    ):
        """
        Adds a single swap and triggers the swap
        """
        self.swap(target_element_id, position, text_html)
        self.triggerSwap()

    def triggerSwap(self):
        if not self.triggered:
            self.triggered = True
            trigger_client_event(
                response=self.response,
                name="jsSwap",  # hx-swap
                params={"swaps": self.swaps},
            )
        else:
            raise ValueError("triggerSwap can only be called once.")


def renderMessagesAsToasts(request, response):
    """
    RPC to tell the WebUI to render django messages as toasts
    """

    text_html = render_to_string("components/messages.html", request=request)
    trigger_client_event(
        response,
        name="renderMessagesAsToasts",
        params=dict(
            swaps=[
                dict(
                    target_element_id="toast_area",
                    text_html=text_html,
                    position="outerHTML",
                )
            ]
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
