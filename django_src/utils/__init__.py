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
