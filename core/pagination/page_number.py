from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPageNumberPagination(PageNumberPagination):
    """
    Page number pagination with ApiResponse format.
    
    Response format:
    {
        "data": [...],
        "pagination": {
            "count": 100,
            "page": 1,
            "page_size": 10,
            "total_pages": 10,
            "next": "http://...",
            "previous": null
        }
    }
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('data', data),
            ('pagination', OrderedDict([
                ('count', self.page.paginator.count),
                ('page', self.page.number),
                ('page_size', self.get_page_size(self.request)),
                ('total_pages', self.page.paginator.num_pages),
                ('next', self.get_next_link()),
                ('previous', self.get_previous_link()),
            ]))
        ]))

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'required': ['data', 'pagination'],
            'properties': {
                'data': schema,
                'pagination': {
                    'type': 'object',
                    'required': ['count', 'page', 'page_size', 'total_pages'],
                    'properties': {
                        'count': {'type': 'integer', 'example': 100},
                        'page': {'type': 'integer', 'example': 1},
                        'page_size': {'type': 'integer', 'example': 10},
                        'total_pages': {'type': 'integer', 'example': 10},
                        'next': {'type': 'string', 'nullable': True, 'format': 'uri'},
                        'previous': {'type': 'string', 'nullable': True, 'format': 'uri'},
                    }
                }
            }
        }
