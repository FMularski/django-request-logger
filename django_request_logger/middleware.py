from django.contrib.auth import get_user_model
from django.conf import settings
from .models import RequestLog
import time
import json


User = get_user_model()


class RequestLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

        self._set_attr_from_settings('REQUEST_LOGGER_METHODS', ['*'])
        self._set_attr_from_settings('REQUEST_LOGGER_STATUS', ['*'])
        self._set_attr_from_settings('REQUEST_LOGGER_EXCLUDE_URL', ['admin'])
        self._set_attr_from_settings('REQUEST_LOGGER_EXCLUDE_CONTENT_TYPE', [])
        self._set_attr_from_settings('REQUEST_LOGGER_SLOW_EXEC_TIME', 500)

    def _set_attr_from_settings(self, attr, value):
        setattr(self, attr, value)
        if hasattr(settings, attr):
            setattr(self, attr, getattr(settings, attr))

    def _skip_save(self, request_log):
        if not '*' in self.REQUEST_LOGGER_METHODS and request_log.method not in self.REQUEST_LOGGER_METHODS:
            return True
        if not '*' in self.REQUEST_LOGGER_STATUS and request_log.status not in self.REQUEST_LOGGER_STATUS:
            return True
        if any(segment in request_log.url for segment in self.REQUEST_LOGGER_EXCLUDE_URL):
            return True
        if any(type_ in request_log.response_content_type for type_ in self.REQUEST_LOGGER_EXCLUDE_CONTENT_TYPE):
            return True
        return False

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        time_start = time.time()

        request_log = RequestLog(
            authenticated_by=request.user if request.user.is_authenticated else None,
            url=request.path,  
            method=request.method,
            body=request.body.decode(),
            headers=str(request.headers).replace("', ", "',\n").replace("{'", "{\n'").replace("'}", "'\n}"),
            client_ip=request.META['REMOTE_ADDR']
        )

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        time_stop = time.time()

        request_log.execution_time = time_stop - time_start
        request_log.is_slow = request_log.execution_time * 1000 > self.REQUEST_LOGGER_SLOW_EXEC_TIME

        request_log.status = response.status_code

        request_log.response_content_type = response.headers['Content-Type']
        request_log.response = response._container[0].decode()

        if 'application/json' in request_log.response_content_type:
            request_log.response = json.loads(request_log.response)
        
        if not self._skip_save(request_log):
            request_log.save()

        return response