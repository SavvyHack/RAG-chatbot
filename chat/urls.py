from django.urls import path
from . import views

urlpatterns = [
    path("", views.chat_page, name="chat_page"),
    path("api/upload_context/", views.upload_context, name="upload_context"),
    path("api/query_rag/", views.query_rag, name="query_rag"),
    path("api/clear_context/", views.clear_context, name="clear_context"),
]