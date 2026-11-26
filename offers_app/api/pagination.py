from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    """Pagination class configuring page size limits for offer list endpoints."""
    
    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 100