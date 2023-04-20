from django.core.management.base import BaseCommand, CommandError
from django_request_logger.models import RequestLog


class Command(BaseCommand):
    help = "Clears RequestLog objects"

    def handle(self, *args, **options):

        logs_to_delete = RequestLog.objects.filter(is_pinned=False)
        count = logs_to_delete.count()
        logs_to_delete.delete()

        return self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} log(s).')) \
            if count else self.stdout.write(self.style.SUCCESS(f'No logs to delete.'))