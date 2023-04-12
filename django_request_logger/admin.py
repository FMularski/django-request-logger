from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import RequestLog
from django.utils.html import format_html, mark_safe


class RequestLogAdmin(ModelAdmin):
    list_display = 'pk', 'created_at', 'method', 'url', 'status'
    list_filter = 'method', 'status'
    search_fields = 'url',

    def get_readonly_fields(self, request, obj):
        fields = [field.name for field in self.model._meta.fields]
        return fields


admin.site.register(RequestLog, RequestLogAdmin)
