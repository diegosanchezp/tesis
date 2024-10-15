from django.core.paginator import Paginator
from django_src.utils import get_page_number

def page_object_list(request, object_list, per_page: int):
    paginator = Paginator(object_list=object_list, per_page=per_page)
    page_number = get_page_number(request)
    page_obj = paginator.get_page(page_number)
    return page_obj
