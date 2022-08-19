from django.conf import settings
from django.core.paginator import Paginator


def pagination(request, objects):
    paginator = Paginator(objects, settings.PAGINATOR_LIMIT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
