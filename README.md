# RAG Chatbot

A Django web app with a simple chat UI that can answer a query two ways:

- **DialoGPT** — a conversational model (`microsoft/DialoGPT-medium`) run locally via Hugging Face `transformers`.
- **Gemini** — Google's Gemini API, called from the server so your API key is never exposed to the browser.

> **Note on the name:** despite "RAG" in the title, this project does not currently retrieve from an external knowledge base — there's no document store, embeddings, or vector search yet. Both buttons are general-purpose chat backends. See [Roadmap](#roadmap) if you want to add real retrieval-augmented generation.

## Features

- Minimal, single-page chat UI (textarea + response panel)
- Local inference with DialoGPT-medium, no external API needed for that path
- Server-side Gemini proxy — your `GEMINI_API_KEY` stays on the server
- Environment-variable based configuration (works the same in dev and production)
- Deployment-ready: Docker, Gunicorn + WhiteNoise, Procfile, and a Render blueprint included

## Tech stack

- Python 3.12, Django 5.1
- Hugging Face `transformers` + PyTorch (local model)
- Gunicorn + WhiteNoise (production server & static files)

## Project structure

```
.
├── chatbot/            # Django project (settings, root URLs, WSGI/ASGI)
├── chat/               # App: chat view + the two model endpoints
│   ├── static/chat/    # main.js, styles.css
│   ├── templates/chat/ # index.html
│   ├── urls.py
│   └── views.py
├── manage.py
├── requirements.txt
├── .env.example        # template for local/prod environment variables
├── Dockerfile
├── Procfile             # for Heroku-style platforms
└── render.yaml          # one-click Render blueprint
```

## Getting started (local development)

**Prerequisites:** Python 3.12+, pip. A [Gemini API key](https://aistudio.google.com/apikey) if you want the Gemini button to work.

```bash
# 1. Clone and enter the project
git clone https://github.com/SavvyHack/RAG-chatbot.git
cd RAG-chatbot

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
# (CPU-only PyTorch keeps this fast/small; skip the first line if you
#  already have a GPU build of torch installed)
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# then edit .env and set GEMINI_API_KEY (and DJANGO_SECRET_KEY)

# 5. Apply migrations and run
python manage.py migrate
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`.

The first request to the DialoGPT button will be slow — the model (~350MB) downloads and loads into memory on first use, then stays cached in the running process for subsequent requests.

## Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DJANGO_SECRET_KEY` | Yes (production) | dev-only fallback | Django's cryptographic signing key |
| `DJANGO_DEBUG` | No | `False` | Enable Django's debug mode (dev only) |
| `DJANGO_ALLOWED_HOSTS` | Yes (production) | `localhost,127.0.0.1` | Comma-separated hostnames allowed to serve this app |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Usually (production) | empty | Comma-separated origins trusted for CSRF, e.g. `https://your-app.onrender.com` |
| `GEMINI_API_KEY` | For the Gemini button | empty | Your Google Gemini API key (server-side only) |
| `GEMINI_MODEL` | No | `gemini-1.5-flash` | Gemini model id to call |

See `.env.example` for a ready-to-copy template.

## Deployment

### Option A: Render (one click via blueprint)

1. Push this repo to your own GitHub account.
2. In Render, choose **New → Blueprint** and point it at the repo (`render.yaml` is already set up).
3. Set the `GEMINI_API_KEY` secret in the Render dashboard when prompted.

### Option B: Docker

```bash
docker build -t rag-chatbot .
docker run -p 8000:8000 \
  -e DJANGO_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))") \
  -e DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1 \
  -e GEMINI_API_KEY=your-key-here \
  rag-chatbot
```

### Option C: Any Heroku-style platform (Procfile)

The included `Procfile` runs migrations on release and serves with Gunicorn:

```
release: python manage.py migrate --noinput
web: gunicorn chatbot.wsgi:application --bind 0.0.0.0:$PORT --log-file -
```

Set the same environment variables listed above on the platform, then push/deploy as usual.

**Memory note:** loading DialoGPT-medium plus PyTorch typically needs 1–2GB of RAM. Free tiers on some platforms are too small for this — size your instance accordingly, or drop the DialoGPT path if you only need Gemini.

## Security notes

A few things worth calling out, since they were fixed as part of getting this deployment-ready:

- **API keys are no longer sent to the browser.** The Gemini key previously round-tripped through a `/get-api-key/` endpoint that returned it as plain JSON to any caller, and the frontend then called Google's API directly. The key now lives only in the server's environment; the frontend calls this app's own `/api/gemini/` endpoint, which proxies the request server-side.
- **Secrets are no longer hardcoded or stored in the database.** `SECRET_KEY` and `GEMINI_API_KEY` come from environment variables (`.env` locally, platform env vars in production), not from source code or a database table.
- **`DEBUG` defaults to `False`**, and `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` are explicit — Django's defaults are for development, not production.
- **`.idea/`, `__pycache__/`, and `db.sqlite3` are git-ignored** so IDE config, compiled bytecode, and local data don't end up in version control.

## Roadmap

Ideas if you want this to become an actual RAG system:

- [ ] Document ingestion (PDF/text/URL loaders)
- [ ] Chunking + embeddings (e.g. `sentence-transformers`) and a vector store (FAISS/Chroma/pgvector)
- [ ] Retrieval step that injects relevant context into the prompt before generation
- [ ] Swap DialoGPT-medium for an instruction-tuned model better suited to Q&A

## License

MIT — see [LICENSE](LICENSE).
