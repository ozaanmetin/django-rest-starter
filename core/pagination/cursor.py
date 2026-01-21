from rest_framework.pagination import CursorPagination


class StandardCursorPagination(CursorPagination):
    """
    Cursor pagination with ApiResponse format.
    Uses CursorPaginatedApiResponse for consistent structure.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100
    ordering = "-created_at"
