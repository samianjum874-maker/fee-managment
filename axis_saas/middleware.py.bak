from django.db import connection
from django.utils.deprecation import MiddlewareMixin
import re

class PublicSchemaMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Saare requests ke liye public schema use karo
        connection.set_schema('public')
        # request.tenant_schema = 'public'
    
    def process_response(self, request, response):
        connection.set_schema('public')
        return response
