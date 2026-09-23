import logging

import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)

# Loaded lazily on first use (see _get_dialogpt) rather than at import
# time, so the Django process itself starts instantly. Importing
# transformers/torch and downloading ~350MB of weights during module
# import used to block every worker at boot, which is exactly the kind
# of delay that fails a platform's startup health check.
_tokenizer = None
_model = None


def _get_dialogpt():
    global _tokenizer, _model
    if _model is None:
        from transformers import AutoModelForCausalLM, AutoTokenizer

        logger.info("Loading microsoft/DialoGPT-medium (first request)...")
        _tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
        _model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
    return _tokenizer, _model


def chat_page(request):
    """Render the chat UI."""
    return render(request, "chat/index.html")


@require_GET
def dialogpt_query(request):
    """Generate a reply locally with DialoGPT-medium."""
    input_text = request.GET.get("query", "").strip()
    if not input_text:
        return JsonResponse({"error": "No input provided"}, status=400)

    tokenizer, model = _get_dialogpt()

    new_input_ids = tokenizer.encode(input_text + tokenizer.eos_token, return_tensors="pt")
    output_ids = model.generate(
        new_input_ids,
        max_length=1000,
        pad_token_id=tokenizer.eos_token_id,
    )
    response_text = tokenizer.decode(
        output_ids[:, new_input_ids.shape[-1] :][0], skip_special_tokens=True
    )
    return JsonResponse({"response": response_text})


@require_GET
def gemini_query(request):
    """Proxy a query to the Gemini API using a server-side API key.

    The API key lives only in this process's environment (GEMINI_API_KEY)
    and is never sent to the browser — the frontend calls this endpoint,
    and this view is the only thing that talks to Google's API.
    """
    input_text = request.GET.get("query", "").strip()
    if not input_text:
        return JsonResponse({"error": "No input provided"}, status=400)

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        logger.error("GEMINI_API_KEY is not set")
        return JsonResponse({"error": "Gemini is not configured on the server"}, status=500)

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.GEMINI_MODEL}:generateContent?key={api_key}"
    )
    payload = {"contents": [{"parts": [{"text": input_text}]}]}

    try:
        api_response = requests.post(url, json=payload, timeout=30)
        api_response.raise_for_status()
        data = api_response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except requests.RequestException:
        logger.exception("Gemini API request failed")
        return JsonResponse({"error": "Failed to reach the Gemini API"}, status=502)
    except (KeyError, IndexError):
        logger.exception("Unexpected Gemini API response shape: %s", data)
        return JsonResponse({"error": "Unexpected response from the Gemini API"}, status=502)

    return JsonResponse({"response": text})
