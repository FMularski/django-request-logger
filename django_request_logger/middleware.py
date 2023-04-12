from django.contrib.auth import get_user_model
from django.conf import settings
from .models import RequestLog
import time


User = get_user_model()


class RequestLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

        self._set_attr_from_settings('REQUEST_LOGGER_METHODS', ['*'])
        self._set_attr_from_settings('REQUEST_LOGGER_STATUS', ['*'])
        self._set_attr_from_settings('REQUEST_LOGGER_EXCLUDE_URL', ['admin'])
        # self._set_attr_from_settings('REQUEST_LOGGER_SKIP_APP', ['admin'])

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
        return False



    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        time_start = time.time()

        request_log = RequestLog(
            authenticated_by=request.user if request.user.is_authenticated else None,
            url=request.path,  
            method=request.method,
            body=request.body.decode() # or request.data
        )

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        time_stop = time.time()

        request_log.execution_time = time_stop - time_start
        request_log.status = response.status_code

        content_type = response.headers['Content-Type']
        
        if 'text/html' in content_type:
            request_log.response = response._container[0].decode()
        elif 'application/json' in content_type:
            request_log.response = 'json'
        else:
            request_log.response = content_type


        
        if not self._skip_save(request_log):
            request_log.save()

        return response