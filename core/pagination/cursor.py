from collections import OrderedDict

from rest_framework.pagination import CursorPagination
from rest_framework.response import Response


class StandardCursorPagination(CursorPagination):
    """
    Cursor pagination with ApiResponse format.
    Better for large datasets and real-time data.
    
    Response format:
    {
        "data": [...],
        "pagination": {
            "page_size": 10,
            "next": "http://...",
            "previous": null
        }
    }
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    ordering = '-created_at'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('data', data),
            ('pagination', OrderedDict([
                ('page_size', self.get_page_size(self.request)),
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
                    'required': ['page_size'],
                    'properties': {
                        'page_size': {'type': 'integer', 'example': 10},
                        'next': {'type': 'string', 'nullable': True, 'format': 'uri'},
                        'previous': {'type': 'string', 'nullable': True, 'format': 'uri'},
                    }
                }
            }
        }
