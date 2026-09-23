from django.db import models  # noqa: F401

# This app is intentionally model-free: API keys and secrets are read from
# environment variables (see chatbot/settings.py and .env.example) rather
# than stored in the database, so there is nothing to define here.
