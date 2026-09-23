FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# build-essential is needed by a couple of transitive ML dependencies at
# install time; it is not needed at runtime but keeping it is simplest.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Use the CPU-only PyTorch build to keep the image small — this app never
# touches a GPU in a typical web deployment.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# DJANGO_SECRET_KEY etc. are provided at runtime; collectstatic only
# needs a value to exist, not a real one, so the settings' dev fallback
# is enough at build time.
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "chatbot.wsgi:application", "--bind", "0.0.0.0:8000"]
