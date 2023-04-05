
from rest_framework.pagination import PageNumberPagination
from rest_framework import pagination
from rest_framework.response import Response


class CustomNumberPagination(PageNumberPagination):

    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):

        if self.page.number < self.page.paginator.num_pages:
            records_in_page = int(self.get_page_size(self.request))
        elif self.page.number == self.page.paginator.num_pages:
            records_in_page = int(
                self.page.paginator.count - ((self.page.number - 1) * self.get_page_size(self.request)))
        else:
            records_in_page = 0
        return Response({
            'pagination': {
                # 'next': self.get_next_link(),
                # 'previous': self.get_previous_link(),
                'count': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'current_page_number': self.page.number,
                'page_size': self.get_page_size(self.request),
                'records_in_page': records_in_page,
                'results': data
            },
        })
