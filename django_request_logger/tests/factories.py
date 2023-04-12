import factory
import faker
from django_request_logger.models import RequestLog

fake = faker.Faker()


class RequestLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RequestLog

    url = '/'
    status = 200
    execution_time = 1