from django.contrib.auth import get_user_model
from django.conf import settings
from datetime import datetime, timedelta
from .models import RequestLog
import time
import json
import re
import os


User = get_user_model()


class RequestLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        self.REQUEST_LOGGER_METHODS = getattr(settings, 'REQUEST_LOGGER_METHODS', ['*'])
        self.REQUEST_LOGGER_STATUS = getattr(settings, 'REQUEST_LOGGER_STATUS', ['*'])
        self.REQUEST_LOGGER_EXCLUDE_URL = getattr(settings, 'REQUEST_LOGGER_EXCLUDE_URL', ['admin'])
        self.REQUEST_LOGGER_EXCLUDE_CONTENT_TYPE = getattr(settings, 'REQUEST_LOGGER_EXCLUDE_CONTENT_TYPE', [])
        self.REQUEST_LOGGER_SLOW_EXEC_TIME = getattr(settings, 'REQUEST_LOGGER_SLOW_EXEC_TIME', 500)
        self.REQUEST_LOGGER_HIDE_SECRETS = getattr(settings, 'REQUEST_LOGGER_HIDE_SECRETS', ['password', 'token', 'access', 'refresh'])
        self.REQUEST_LOGGER_CLEAR_LOGS_TIME = getattr(settings, 'REQUEST_LOGGER_CLEAR_LOGS_TIME', None)
        self.REQUEST_LOGGER_LOG_FILES_PATH = getattr(settings, 'REQUEST_LOGGER_LOG_FILES_PATH', None)
        self.REQUEST_LOGGER_LOG_FILES_FIELDS = getattr(settings, 'REQUEST_LOGGER_LOG_FILES_FIELDS', ['created_at', 'client_ip', 'method', 'url', 'status'])

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
    
    def _apply_new_lines(self, s):
        return s \
            .replace('{', '{\n') \
            .replace('}', '\n}') \
            .replace('[', '[\n') \
            .replace(']', '\n]') \
            .replace(", '", ",\n'") \
            .replace("'", '"')
    
    def _hide_secrets(self, request_log):
        body_content_type = request_log.body_content_type
        body = request_log.body

        if body_content_type == 'application/json':
            for secret in self.REQUEST_LOGGER_HIDE_SECRETS:
                body = re.sub(f'"{secret}": ".*?"', f'"{secret}": "*** hidden ***"', body)
        elif body_content_type == 'application/xml':
            for secret in self.REQUEST_LOGGER_HIDE_SECRETS:
                body = re.sub(f'<{secret}>.*?</{secret}>', f'<{secret}>*** hidden ***</{secret}>', body)
        elif body_content_type == 'application/x-www-form-urlencoded':
            body += '&'
            for secret in self.REQUEST_LOGGER_HIDE_SECRETS:
                body = re.sub(f'{secret}=.*?&', f'{secret}=*** hidden ***&', body)
            
        request_log.body = body

        response = request_log.response if type(request_log.response) == str else str(request_log.response)
        if request_log.response_content_type == 'application/json':
            for secret in self.REQUEST_LOGGER_HIDE_SECRETS:
                response = re.sub(f"'{secret}': '.*?'", f"'{secret}': '*** hidden ***'", response)
            response = self._apply_new_lines(response)
        request_log.response = response

    def _clear_old_logs(self):
        RequestLog.objects.filter(
            created_at__lte=datetime.now() - timedelta(minutes=self.REQUEST_LOGGER_CLEAR_LOGS_TIME), 
            is_pinned=False
        ).delete()

    def _dump_to_file(self, request_log):
        path = self.REQUEST_LOGGER_LOG_FILES_PATH
        if not os.path.exists(path):
            os.makedirs(path)

        with open(f'{path}/{datetime.now().date()}.log', 'a') as log_file:
            fields = self.REQUEST_LOGGER_LOG_FILES_FIELDS
            log_line = ' '.join([str(getattr(request_log, field)).replace('\n', '') for field in fields]) + '\n'           
            log_file.write(log_line)

    def __call__(self, request):
        time_start = time.time()

        request_log = RequestLog(
            authenticated_by=request.user if request.user.is_authenticated else None,
            url=request.path,  
            method=request.method,
            body=request.body.decode(),
            body_content_type=request.headers.get('Content-Type'),
            headers=self._apply_new_lines(str(request.headers)),
            client_ip=request.META['REMOTE_ADDR']
        )

        response = self.get_response(request)

        time_stop = time.time()

        request_log.execution_time = time_stop - time_start
        request_log.is_slow = request_log.execution_time * 1000 > self.REQUEST_LOGGER_SLOW_EXEC_TIME

        request_log.status = response.status_code

        request_log.response_content_type = response.headers['Content-Type']
        request_log.response = response._container[0].decode()

        if 'application/json' in request_log.response_content_type:
            request_log.response = json.loads(request_log.response)
        
        self._hide_secrets(request_log)

        if not self._skip_save(request_log):
            request_log.save()

            if self.REQUEST_LOGGER_LOG_FILES_PATH:
                self._dump_to_file(request_log)

        if self.REQUEST_LOGGER_CLEAR_LOGS_TIME:
            self._clear_old_logs()

        return response