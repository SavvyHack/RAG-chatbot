"""
URL configuration for the chatbot project.

The `urlpatterns` list routes URLs to views. For more information see:
https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("chat.urls")),
    path("admin/", admin.site.urls),
]
