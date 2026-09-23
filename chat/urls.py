from django.urls import path

from . import views

urlpatterns = [
    path("", views.chat_page, name="chat_page"),
    path("api/dialogpt/", views.dialogpt_query, name="dialogpt_query"),
    path("api/gemini/", views.gemini_query, name="gemini_query"),
]
