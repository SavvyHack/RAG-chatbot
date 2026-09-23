release: python manage.py migrate --noinput
web: gunicorn chatbot.wsgi:application --bind 0.0.0.0:$PORT --log-file -
