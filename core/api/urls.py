from django.urls import path
from .views import *


urlpatterns = [
    path('users/', UserListView.as_view(), name='users'),
    path('users/<pk>/', UserDetailView.as_view(), name='user'),
]
