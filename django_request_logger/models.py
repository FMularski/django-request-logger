from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class HttpMethodChoices(models.TextChoices):
    GET = 'GET', 'GET'
    POST = 'POST', 'POST'
    PUT = 'PUT', 'PUT'
    PATCH = 'PATCH', 'PATCH'
    DELETE = 'DELETE', 'DELETE'
    CONNECT = 'CONNECT', 'CONNECT'
    HEAD = 'HEAD', 'HEAD'
    OPTIONS = 'OPTIONS', 'OPTIONS'
    TRACE = 'TRACE', 'TRACE'


class RequestLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    authenticated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    url = models.CharField(max_length=200)
    method = models.CharField(max_length=7, choices=HttpMethodChoices.choices)
    status = models.PositiveSmallIntegerField()
    body = models.JSONField(null=True, blank=True)
    response = models.JSONField(null=True, blank=True)
    response_content_type = models.CharField(max_length=200)
    execution_time = models.FloatField()

    def __str__(self):
        return f'[{self.created_at.strftime("%m/%d/%Y, %H:%M:%S")}] {self.method} {self.url}'

