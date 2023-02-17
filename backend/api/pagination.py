from rest_framework import pagination
from rest_framework.response import Response


class OnlyDataPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(data)


class LimitPagination(pagination.PageNumberPagination):
    page_size_query_param = "6"
