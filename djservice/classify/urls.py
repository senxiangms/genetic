from django.urls import path

from . import views
from rest_framework import routers
from django.contrib.auth.models import User

urlpatterns = [
    path("", views.index, name="index"),
    path("diagnose", views.diagnose, name="diagnose")
]