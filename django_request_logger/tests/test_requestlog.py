import pytest


@pytest.mark.django_db
def test_create_request_log(client, request_log_factory):
    request_log = request_log_factory()
    assert request_log.url == '/'