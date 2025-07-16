from rest_framework import pagination


class CommonPagination(pagination.PageNumberPagination):
    page_size = 7  # default page size
    page_size_query_param = 'page_size'
    max_page_size = 100  # optional limit to prevent excessively large page sizes
