from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin
from django.contrib.admin.actions import delete_selected as default_delete_selected
from .models import RequestLog
from datetime import datetime


def delete_selected(modeladmin, request, queryset):
    response = default_delete_selected(modeladmin, request, queryset)
    storage = messages.get_messages(request)
    try:
        del storage._queued_messages[-1]
    except:
        pass
    return response


class RequestLogAdmin(ModelAdmin):
    list_filter = 'method', 'status', 'created_at', 'response_content_type', 'is_slow'
    search_fields = 'url', 'client_ip'
    list_per_page = 20
    ordering = '-is_pinned', '-created_at',
    actions = 'pin', 'delete_selected'

    change_list_template = 'admin/django_request_logger/requestlog/change_list.html'

    def changelist_view(self, request, extra_context = {}):
        requests_500 = RequestLog.objects.filter(status__gte=500).order_by('-pk')[:5]
        extra_context['requests_500'] = requests_500

        requests_slow = RequestLog.objects.filter(is_slow=True).order_by('-pk')[:5]
        extra_context['requests_slow'] = requests_slow

        statuses = RequestLog.objects.values_list('status', flat=True).distinct()
        status_summaries = []
        
        for status in statuses:
           status_requests = RequestLog.objects.filter(status=status)
           total_count = status_requests.count()
           today_count = status_requests.filter(created_at__date=datetime.now().date()).count()
           status_summaries += [{'status': status, 'total_count': total_count, 'today_count': today_count}]
        
        extra_context['status_summaries'] = status_summaries

        clients = RequestLog.objects.values_list('client_ip', flat=True).distinct()
        extra_context['clients'] = clients.count()

        return super().changelist_view(request, extra_context)

    def headers_content(self, obj):
        return obj.headers

    def body_content(self, obj):
        return obj.body

    def response_content(self, obj):
        return obj.response
    
    def get_list_display(self, request):
        list_display = 'created_at', 'authenticated_by', 'method', 'url', 'status',
        if RequestLog.objects.filter(is_pinned=True).exists():
            list_display += 'is_pinned',
        return list_display
        
    def get_fields(self, request, obj):
        fields = [field.name for field in self.model._meta.fields] + ['headers_content', 'body_content', 'response_content']
        fields.remove('headers')
        fields.remove('body')
        fields.remove('response')
        return fields

    def get_readonly_fields(self, request, obj):
        readonly_fields = self.get_fields(request, obj)
        readonly_fields.remove('is_pinned')
        return readonly_fields

    def has_add_permission(self, request, obj=None):
        return False
    
    def delete_queryset(self, request, queryset):
        logs_to_delete = queryset.filter(is_pinned=False)
        logs_pinned = queryset.filter(is_pinned=True)
        self.message_user(request, f'Successfully deleted {logs_to_delete.count()} request log(s).', level=messages.SUCCESS)
        if logs_pinned:
            self.message_user(request, f'Could not delete {logs_pinned.count()} pinned request log(s).', level=messages.WARNING)

        return super().delete_queryset(request, logs_to_delete)
    
    def delete_model(self, request, obj) -> None:
        if obj.is_pinned:
            self.message_user(request, 'You cannot delete a pinned request log.', level=messages.WARNING)
            return None
        self.message_user(request, 'Request log successfully deleted.', level=messages.SUCCESS)
        return super().delete_model(request, obj)

    def response_delete(self, request, obj_display, obj_id):
        response = super().response_delete(request, obj_display, obj_id)
        storage = messages.get_messages(request)
        del storage._queued_messages[-1]
        return response

    @admin.action(description='Pin/Unpin selected request logs')
    def pin(self, request, queryset):
        for log in queryset.all():
            log.is_pinned = not log.is_pinned
            log.save()
        
        self.message_user(request, f'Altered {queryset.count()} log(s).', messages.SUCCESS)

    def get_actions(self, request):
        actions = super().get_actions(request)
        self.actions += delete_selected,
        return actions

admin.site.register(RequestLog, RequestLogAdmin)
