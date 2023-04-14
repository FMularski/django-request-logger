from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import RequestLog
import json


class RequestLogAdmin(ModelAdmin):
    list_display = 'created_at', 'authenticated_by', 'method', 'url', 'status', 'response_content_type'
    list_filter = 'method', 'status', 'response_content_type', 'is_slow'
    search_fields = 'url',

    def headers_content(self, obj):
        return obj.headers

    def body_content(self, obj):
        return obj.body

    def response_content(self, obj):
        if 'application/json' in obj.response_content_type:
            return json.dumps(obj.response, indent=4)
        return obj.response
    
    def get_fields(self, request, obj):
        fields = [field.name for field in self.model._meta.fields] + ['headers_content', 'body_content', 'response_content']
        fields.remove('headers')
        fields.remove('body')
        fields.remove('response')
        return fields

    def get_readonly_fields(self, request, obj):
        return self.get_fields(request, obj)


admin.site.register(RequestLog, RequestLogAdmin)
