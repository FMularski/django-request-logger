from django.contrib.auth import get_user_model
from .models import RequestLog
import time


User = get_user_model()


class RequestLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        time_start = time.time()

        request_log = RequestLog(
            authenticated_by=request.user if type(request.user) == User else None,
            url=request.path,  
            method=request.method,
            body=request.body.decode() # or request.data
        )

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        time_stop = time.time()

        request_log.execution_time = time_stop - time_start
        request_log.response = response.headers['Content-Type']
        request_log.status = response.status_code
    
        # if 'admin' not in request_log.url:
        request_log.save()

        return response