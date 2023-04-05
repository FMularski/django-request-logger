# Generated by Django 4.2 on 2023-04-05 14:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('django_request_logger', '0001_initial'), ('django_request_logger', '0002_requestlog_execution_time_requestlog_method')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('url', models.CharField(max_length=200)),
                ('status', models.PositiveSmallIntegerField()),
                ('body', models.JSONField(blank=True, null=True)),
                ('response', models.JSONField(blank=True, null=True)),
                ('authenticated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('execution_time', models.FloatField(default=0)),
                ('method', models.CharField(choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT'), ('PATCH', 'PATCH'), ('DELETE', 'DELETE'), ('CONNECT', 'CONNECT'), ('HEAD', 'HEAD'), ('OPTIONS', 'OPTIONS'), ('TRACE', 'TRACE')], default='GET', max_length=7)),
            ],
        ),
    ]
