from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import RequestLog


class RequestLogAdmin(ModelAdmin):
    list_display = 'pk', 'created_at', 'method', 'url', 'status'
    list_filter = 'method', 'status'
    search_fields = 'url',

    def get_readonly_fields(self, request, obj):
        return [field.name for field in self.model._meta.fields]


admin.site.register(RequestLog, RequestLogAdmin)
