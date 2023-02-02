from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """
    Custom pagination for api

    :param PageNumberPagination: resframework base PageNumberPagination
    :type PageNumberPagination: rest_framework.pagination.PageNumberPagination
    """
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000
