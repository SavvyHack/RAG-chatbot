from django.test import TestCase
from django.urls import reverse
import json

class ChatPageTests(TestCase):
    def test_chat_page_loads(self):
        response = self.client.get(reverse("chat_page"))
        self.assertEqual(response.status_code, 200)

    def test_upload_context_requires_post(self):
        response = self.client.get(reverse("upload_context"))
        self.assertEqual(response.status_code, 405) # Method Not Allowed

    def test_query_rag_requires_input(self):
        response = self.client.post(
            reverse("query_rag"),
            data=json.dumps({}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_clear_context(self):
        response = self.client.post(reverse("clear_context"))
        self.assertEqual(response.status_code, 200)