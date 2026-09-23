from django.test import TestCase
from django.urls import reverse


class ChatPageTests(TestCase):
    def test_chat_page_loads(self):
        response = self.client.get(reverse("chat_page"))
        self.assertEqual(response.status_code, 200)

    def test_dialogpt_query_requires_input(self):
        response = self.client.get(reverse("dialogpt_query"))
        self.assertEqual(response.status_code, 400)

    def test_gemini_query_requires_input(self):
        response = self.client.get(reverse("gemini_query"))
        self.assertEqual(response.status_code, 400)
